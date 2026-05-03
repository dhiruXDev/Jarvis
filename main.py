from core.listener import listen
from core.speaker import speak
from core.brain import process
from utils.executor import execute

def main():
    speak("Jarvis is ready")

    while True:
        command = listen()

        if not command:
            continue

        speak("I heard you")   # ✅ ADD THIS

        intent = process(command)

        if intent["intent"] == "exit":
            speak("Goodbye")
            break

        execute(intent)

if __name__ == "__main__":
    main()