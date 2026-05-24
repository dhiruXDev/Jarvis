from queue import Queue
from threading import Thread, Event
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor

from core.listener import listen
from core.speaker import speak
from core.brain import process
from core.server import run_web_server

from modules.multilang import translator
from utils.executor import execute


# ==========================================
# GLOBALS
# ==========================================

# Shared command queue
command_queue = Queue()

# Background worker pool
executor = ThreadPoolExecutor(max_workers=3)

# Keep app alive
stop_event = Event()


# ==========================================
# LISTENER THREAD
# ==========================================

def listener_loop():

    while not stop_event.is_set():

        try:

            command = listen()

            if command:

                print(f"\nUser: {command}")

                command_queue.put(command)

        except Exception as e:

            print("Listener Error:", e)


# ==========================================
# PROCESS COMMAND
# ==========================================

def process_command(command):

    try:

        # -------------------------
        # NORMALIZE & FAST PARSE
        # -------------------------
        normalized = translator.normalize_hinglish(command)
        from core.local_parser import local_parse
        intent = local_parse(normalized)
        lang = "en"

        if not intent:
            # -------------------------
            # LANGUAGE DETECTION & TRANSLATION
            # -------------------------
            lang = translator.detect_lang(normalized)

            if lang != "en":
                text_en = translator.to_english(command)
                print("Translated:", text_en)
            else:
                text_en = normalized

            # -------------------------
            # AI INTENT PARSING
            # -------------------------
            intent = process(text_en)
            print("Intent:", intent)
        else:
            print("Intent (Fast Track):", intent)

        # -------------------------
        # EXIT
        # -------------------------

        if intent.get("intent") == "system" and intent.get("action") == "exit":

            final = translator.from_english(
                "Goodbye",
                lang
            )

            speak(final)

            stop_event.set()

            return

        # -------------------------
        # EXECUTE TASK
        # -------------------------

        result = execute(intent, lang)

        print("Result:", result)

        # -------------------------
        # SPEAK RESULT
        # -------------------------

        if isinstance(result, str):

            final = translator.from_english(
                result,
                lang
            )

            speak(final)

    except Exception as e:

        print("Process Error:", e)


# ==========================================
# DISPATCHER THREAD
# ==========================================

def dispatcher_loop():

    while not stop_event.is_set():

        try:

            command = command_queue.get()

            # RUN TASK IN BACKGROUND
            executor.submit(
                process_command,
                command
            )

        except Exception as e:

            print("Dispatcher Error:", e)


# ==========================================
# MAIN
# ==========================================

def main():

    print("\nStarting Jarvis...\n")

    # -------------------------
    # START WEB SERVER THREAD
    # -------------------------
    server_thread = Thread(
        target=run_web_server,
        args=(8000, command_queue),
        daemon=True
    )
    server_thread.start()

    # -------------------------
    # LAUNCH BROWSER THREAD
    # -------------------------
    def launch_browser():
        time.sleep(1.2)
        webbrowser.open("http://localhost:8000")

    Thread(target=launch_browser, daemon=True).start()

    speak("Jarvis is ready")

    # -------------------------
    # START LISTENER THREAD
    # -------------------------

    listener_thread = Thread(
        target=listener_loop,
        daemon=True
    )

    listener_thread.start()

    # -------------------------
    # START DISPATCHER THREAD
    # -------------------------
    dispatcher_thread = Thread(
        target=dispatcher_loop,
        daemon=True
    )
    dispatcher_thread.start()
    print("Jarvis Running...\n")
    
    # -------------------------
    # KEEP MAIN THREAD ALIVE
    # -------------------------
    stop_event.wait()


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()