import threading
import time


def set_reminder(message, seconds):

    def reminder():

        time.sleep(seconds)

        print(f"\nREMINDER: {message}")

    thread = threading.Thread(
        target=reminder
    )

    thread.daemon = True

    thread.start()

    return (
        f"Reminder set for "
        f"{seconds} seconds"
    )