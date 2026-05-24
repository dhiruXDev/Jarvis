# pyrefly: ignore [missing-import]
import pyttsx3
from queue import Queue
from threading import Thread, Event

speech_queue = Queue()
is_speaking = Event()

def _speak_worker():
<<<<<<< HEAD
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
        
=======
    # Initialize engine in the background thread for COM safety
    try:
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 170)
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
    except Exception as e:
        speak("Failed to initialize TTS engine:", e)
        engine = None

>>>>>>> 215477246292bf6fa7caa533fd02bfc4241891b8
    while True:
        text = speech_queue.get()
        print(f"[SPEAKER WORKER] Received text from queue: '{text}'")
        if text is None:  # stop signal
            break

        if engine is None:
            continue

        try:
<<<<<<< HEAD
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
=======
            is_speaking.set()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            speak("Speech error:", e)
        finally:
            if speech_queue.empty():
                is_speaking.clear()
>>>>>>> 215477246292bf6fa7caa533fd02bfc4241891b8

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
<<<<<<< HEAD
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
=======
    speak("Jarvis:", text)
    is_speaking.set()
    speech_queue.put(text)
>>>>>>> 215477246292bf6fa7caa533fd02bfc4241891b8
