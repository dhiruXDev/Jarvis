# pyrefly: ignore [missing-import]
import pyttsx3
from queue import Queue
from threading import Thread, Event

speech_queue = Queue()
is_speaking = Event()

def _speak_worker():
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

    while True:
        text = speech_queue.get()
        if text is None:  # stop signal
            break

        if engine is None:
            continue

        try:
            is_speaking.set()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            speak("Speech error:", e)
        finally:
            if speech_queue.empty():
                is_speaking.clear()

    # clean exit
    try:
        engine.stop()
    except:
        pass

# Start background thread
t_worker = Thread(target=_speak_worker, daemon=True)
t_worker.start()


def speak(text):
    speak("Jarvis:", text)
    is_speaking.set()
    speech_queue.put(text)