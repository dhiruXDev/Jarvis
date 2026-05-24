import time
import speech_recognition as sr
<<<<<<< HEAD
from core.server import mic_state, set_hud_status, broadcast_event
=======
from core.speaker import is_speaking
>>>>>>> 215477246292bf6fa7caa533fd02bfc4241891b8

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

calibrated = False


def listen():
<<<<<<< HEAD
    # If Jarvis is currently speaking, do not open the mic to avoid audio hardware conflict and self-hearing
    from core.server import status_state
    if status_state.get("state") == "speaking":
        time.sleep(0.2)
        return ""

    # If microphone has been deactivated via the frontend UI controls
    if not mic_state.get("active", True):
        time.sleep(0.5)
        return ""

    try:
        with sr.Microphone() as source:
            # Broadcast state change to the browser
            set_hud_status("listening")

            # Adjust briefly for ambient noise (non-blocking feel)
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            # Listen with phrase limits to keep responses snappy
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

            # Broadcast thinking/recognizing state
            set_hud_status("recognizing")

            command = recognizer.recognize_google(audio)
            
            if command.strip():
                # Stream the user's recognized text bubble to the UI conversation
                timestamp = time.strftime("%I:%M %p")
                broadcast_event("chat_message", {
                    "sender": "You",
                    "text": command,
                    "timestamp": timestamp
                })
                return command.lower().strip()
                
            return ""

    except sr.WaitTimeoutError:
        # Listening timed out without voice input, return to idle
        set_hud_status("idle")
        return ""

    except sr.UnknownValueError:
        # Sound captured but speech not understood
        set_hud_status("idle")
        return ""

    except Exception as e:
        # Graceful degradation if PyAudio/microphone is missing or locked
        # Let's print the status and return to idle so keyboard remains fully functional
        set_hud_status("idle")
        # Standard print captures and streams to UI terminal drawer automatically!
        print(f"Microphone: inactive/offline ({str(e)})")
        time.sleep(1.5)
=======
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
>>>>>>> 215477246292bf6fa7caa533fd02bfc4241891b8
        return ""