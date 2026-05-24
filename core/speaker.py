# import pyttsx3

# engine = pyttsx3.init()
# engine.setProperty('rate', 170)

# def speak(text):
#     print(f"Jarvis: {text}")
#     engine.say(text)
#     engine.runAndWait()

# import pyttsx3

# engine = pyttsx3.init()

# def speak(text):
#     try:
#         print("Jarvis:", text)
#         engine.say(text)
#         engine.runAndWait()
#     except:
#         print("Speech error")

import pyttsx3
from queue import Queue
from threading import Thread

speech_queue = Queue()

def _speak_worker():
    from core.server import set_hud_status
    import pythoncom
    import win32com.client
    
    # Initialize COM once for this worker thread
    pythoncom.CoInitialize()
    
    speaker = None
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 1
        print("[SPEAKER WORKER] SAPI SpVoice initialized successfully.")
    except Exception as sapi_init_err:
        print("[SPEAKER WORKER] Failed to initialize SAPI SpVoice:", sapi_init_err)
        
    while True:
        text = speech_queue.get()
        print(f"[SPEAKER WORKER] Received text from queue: '{text}'")
        if text is None:  # stop signal
            break

        try:
            set_hud_status("speaking")
            success = False
            
            if speaker is not None:
                try:
                    print(f"[SPEAKER WORKER] Calling SAPI Speak (async) for: '{text}'")
                    speaker.Speak(text, 1)  # 1 = SVSFlagsAsync
                    
                    # Cooperatively wait for speech completion to avoid thread blocks and allow GIL release
                    import time
                    while not speaker.WaitUntilDone(100):
                        time.sleep(0.05)
                        
                    print(f"[SPEAKER WORKER] SAPI Speak completed for: '{text}'")
                    success = True
                except Exception as sapi_err:
                    print("[SPEAKER WORKER] Native SAPI Speak failed:", sapi_err)

            # Fallback to pyttsx3 (initialized per request to prevent event loop thread hang)
            if not success:
                try:
                    print(f"[SPEAKER WORKER] Calling pyttsx3 fallback for: '{text}'")
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 170)
                    voices = engine.getProperty('voices')
                    if voices:
                        engine.setProperty('voice', voices[0].id)
                    engine.say(text)
                    engine.runAndWait()
                    engine.stop()
                    del engine
                    print(f"[SPEAKER WORKER] pyttsx3 fallback completed for: '{text}'")
                except Exception as pyttsx_err:
                    print("[SPEAKER WORKER] TTS fallback error:", pyttsx_err)
            
            set_hud_status("idle")
            print(f"[SPEAKER WORKER] Finished processing text: '{text}'")
        except Exception as e:
            print("[SPEAKER WORKER] General error:", e)
            set_hud_status("idle")
            
    pythoncom.CoUninitialize()

# Start background thread
t_worker = Thread(target=_speak_worker, daemon=True)
t_worker.start()


def speak(text):
    print("Jarvis:", text)
    speech_queue.put(text)

    # Broadcast Jarvis response bubble to the UI conversation feed
    import time
    from core.server import broadcast_event
    timestamp = time.strftime("%I:%M %p")
    broadcast_event("chat_message", {
        "sender": "Jarvis",
        "text": text,
        "timestamp": timestamp
    })
