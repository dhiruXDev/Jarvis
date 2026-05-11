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

engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)
speech_queue = Queue()

def _speak_worker():
    while True:
        text = speech_queue.get()
        if text is None:  # stop signal
            break

        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("Speech error:", e)

    # clean exit
    try:
        engine.stop()
    except:
        pass

# Start background thread
t_worker = Thread(target=_speak_worker, daemon=True)
t_worker.start()


def speak(text):
    print("Jarvis:", text)
    speech_queue.put(text)