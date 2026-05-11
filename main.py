# from core.listener import listen
# from core.speaker import speak
# from modules.multilang import translator
# from core.brain import process
# from utils.executor import execute
# from queue import Queue
# from threading import Thread
# from core.listener import listen
# from core.brain import process
# from core.task_manager import task_manager
# from core.speaker import speak
# from concurrent.futures import ThreadPoolExecutor

# command_queue = Queue()
# executor = ThreadPoolExecutor(max_workers=5)

# def listen_worker():
#     while True:
#         try: 
#             command = listen()
#             if command:
#                 command_queue.put(command)
#         except Exception as e:
#             print("Listen Error: ", e)

# def process_worker(command):
#     try:
#         lang = translator.detect_lang(command)
#         text_en = translator.to_english(command)
#         print("Translated:", text_en)
#         intent = process(text_en)
#         print("Intent:", intent)
#         if intent.get("intent") == "exit":
#             final = translator.from_english(
#                 "Goodbye",
#                 lang
#             )
#             speak(final)
#             exit()
#         # Execute Task
#         result = execute(intent, lang)
#         print("Result:", result)
#         # Speak Result
#         if isinstance(result, str):
#             final = translator.from_english(
#                 result,
#                 lang
#             )
#             speak(final)

#     except Exception as e:
#         print("Process Error:", e)

# def dispatcher_loop():
#     while True:
#         command = command_queue.get()
#         if command:
#             lang = translator.detect_lang(command)
#             text_en = translator.to_english(command)
#             intent = process(text_en)
#             result = execute(intent, lang)
#             task_manager.add_task(lambda: speak(result))
#         executor.submit(process_worker, command)

#     speak("Jarvis is ready")

#     while True:
#         # user_text = translator.listen()
#         user_text = input("User: ")
#         if not user_text:
#             continue

#         # 🌍 detect + translate
#         lang = translator.detect_lang(user_text)
#         text_en = translator.to_english(user_text)

#         # 🧠 AI intent
#         intent = process(text_en)

#         if intent["intent"] == "exit":
#             translator.speak("Goodbye", lang)
#             break

#         # ⚙️ execute (you can return a message from execute)
#         result = execute(intent, lang)
#         print('Jarvis: ', result)

#         # 🔊 speak result (translate back)
#         if isinstance(result, str):
#             final = translator.from_english(result, lang)
#             translator.speak(final, lang)
#         # else:
#         #     # fallback message
#         #     translator.speak(
#         #         translator.from_english("Done.", lang),
#         #         lang
#         #     )

# def main():
#     speak("Jarvis is ready")
#     listen_thread = Thread(target=listen_worker, daemon=True)
#     dispatcher_thread = Thread(target=dispatcher_loop, daemon=True)
#     listen_thread.start()
#     dispatcher_thread.start()
#     listen_thread.join()
#     dispatcher_thread.join()

# if __name__ == "__main__":
#     main()

from queue import Queue
from threading import Thread, Event
from concurrent.futures import ThreadPoolExecutor

from core.listener import listen
from core.speaker import speak
from core.brain import process

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
        # LANGUAGE DETECTION
        # -------------------------

        lang = translator.detect_lang(command)

        # -------------------------
        # TRANSLATE TO ENGLISH
        # -------------------------

        text_en = translator.to_english(command)

        print("Translated:", text_en)

        # -------------------------
        # AI INTENT PARSING
        # -------------------------

        intent = process(text_en)

        print("Intent:", intent)

        # -------------------------
        # EXIT
        # -------------------------

        if intent.get("intent") == "exit":

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