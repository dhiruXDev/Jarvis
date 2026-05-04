from core.listener import listen
from core.speaker import speak
from modules.multilang import translator
from core.brain import process
from utils.executor import execute

def main():
    speak("Jarvis is ready")

    while True:
        # user_text = translator.listen()
        user_text = input("User: ")
        if not user_text:
            continue

        # 🌍 detect + translate
        lang = translator.detect_lang(user_text)
        text_en = translator.to_english(user_text)

        # 🧠 AI intent
        intent = process(text_en)

        if intent["intent"] == "exit":
            translator.speak("Goodbye", lang)
            break

        # ⚙️ execute (you can return a message from execute)
        result = execute(intent, lang)

        # 🔊 speak result (translate back)
        # if isinstance(result, str):
        #     final = translator.from_english(result, lang)
        #     translator.speak(final, lang)
        # else:
        #     # fallback message
        #     translator.speak(
        #         translator.from_english("Done.", lang),
        #         lang
            # )

if __name__ == "__main__":
    main()