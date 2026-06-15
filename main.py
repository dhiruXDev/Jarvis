from queue import Queue
from threading import Thread, Event
import time
import webbrowser
import os
import subprocess
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
            # Speak immediate filler response to user to avoid dead silence while querying LLM
            import random
            fillers = [
                "Just a second, let me check.",
                "One moment, working on it.",
                "Let me look into that for you.",
                "Give me a moment to think."
            ]
            speak(random.choice(fillers))

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
        if isinstance(intent, dict):
            intent["raw_query"] = command

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
    # VERIFY OLLAMA CONNECTION
    # -------------------------
    def verify_ollama():
        print("[SYSTEM] Verifying Ollama connection in background...")
        try:
            # pyrefly: ignore [missing-import]
            import ollama
            ollama.list()
            print("[SYSTEM] Ollama connection verified successfully.")
        except Exception as e:
            print(f"[SYSTEM] Ollama connection warning: {e}")

    # Verify connection in background thread to prevent startup delay
    Thread(target=verify_ollama, daemon=True).start()

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
    # KEEP MAIN THREAD ALIVE / LAUNCH ELECTRON
    # -------------------------
    if not os.environ.get("ELECTRON_RUNNING"):
        from core.server import web_server_ready, web_server_port
        print("[SYSTEM] Waiting for web server to start...")
        if web_server_ready.wait(timeout=10):
            port = web_server_port or 8000
            print(f"[SYSTEM] Web server ready on port {port}. Launching Electron desktop app...")
            env = os.environ.copy()
            env["ELECTRON_RUNNING"] = "1"
            env["JARVIS_PORT"] = str(port)
            try:
                # Spawn Electron subprocess
                electron_proc = subprocess.Popen(
                    "npm start",
                    shell=True,
                    env=env,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                # Monitor Electron and shut down the backend when Electron exits
                def monitor_electron():
                    electron_proc.wait()
                    print("[SYSTEM] Electron desktop app closed. Stopping Jarvis backend...")
                    stop_event.set()
                
                Thread(target=monitor_electron, daemon=True).start()
            except Exception as e:
                print(f"[SYSTEM] Failed to start Electron: {e}")
        else:
            print("[SYSTEM] Web server startup timed out. Cannot start Electron.")

    stop_event.wait()


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()