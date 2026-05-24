import speech_recognition as sr
from core.speaker import is_speaking

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

calibrated = False


def listen():
    global calibrated

    try:
        # Wait for speaker to finish before starting to listen
        if is_speaking.is_set():
            is_speaking.wait()

        with sr.Microphone() as source:
            if not calibrated:
                speak("Calibrating microphone for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                calibrated = True
                speak("Calibration complete.")

            speak("Listening...")
            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=8
            )

        # Discard audio if Jarvis started speaking during the audio capture
        if is_speaking.is_set():
            return ""

        speak("Recognizing...")
        command = recognizer.recognize_google(audio, language="hi-IN")
        return command.lower()

    except sr.WaitTimeoutError:
        return ""

    except sr.UnknownValueError:
        return ""

    except Exception as e:
        speak("Listener Error:", e)
        return ""