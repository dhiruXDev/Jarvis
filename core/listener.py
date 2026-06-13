from core.speaker import is_speaking , speak
import time

from core.server import mic_state, set_hud_status, broadcast_event
# pyrefly: ignore [missing-import]
import speech_recognition as sr

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

calibrated = False


def listen():
    # If Jarvis is currently speaking, do not open the mic to avoid audio hardware conflict and self-hearing
    from core.server import status_state
    if is_speaking.is_set() or status_state.get("state") == "speaking":
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
        return ""
