import threading
import time


def set_reminder(message, seconds):

    def reminder():

        time.sleep(seconds)

        speak(f"\nREMINDER: {message}")
        from core.speaker import speak
        speak(f"Reminder: {message}")

    thread = threading.Thread(
        target=reminder
    )

    thread.daemon = True

    thread.start()

    return (
        f"Reminder set for "
        f"{seconds} seconds"
    )