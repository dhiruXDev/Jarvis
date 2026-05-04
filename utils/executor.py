 
# from core.speaker import speak
# import actions.system as system
# import actions.typing as typing
# import webbrowser

# def execute(intent):
#     if intent["intent"] == "open_app":
#         speak(f"Opening {intent['target']}")
#         system.open_app(intent["target"])

#     elif intent["intent"] == "type":
#         speak("Typing now")
#         typing.type_text(intent["text"])

#     elif intent["intent"] == "exit":
#         speak("Shutting down")
#         return False

#     elif intent["intent"] == "search":
#         speak("Searching now")
#         webbrowser.open(f"https://www.google.com/search?q={intent['query']}")
    
#     else:
#         speak("I did not understand")

#     return True

import actions.system as system
import actions.typing as typing
import webbrowser
from modules.multilang import translator

def execute(intent, lang="en"):
    if intent["intent"] == "open_app":
        msg = f"Opening {intent['target']} now"
        translated = translator.from_english(msg, lang)
        translator.speak(translated, lang)

        system.open_app(intent["target"])
        return msg

    elif intent["intent"] == "type":
        msg = "I am typing now"
        translated = translator.from_english(msg, lang)
        translator.speak(translated, lang)

        typing.type_text(intent["text"])
        return msg

    elif intent["intent"] == "search":
        msg = f"I am searching {intent['query']}"
        translated = translator.from_english(msg, lang)
        translator.speak(translated, lang)


        webbrowser.open(f"https://www.google.com/search?q={intent['query']}")
        return msg

    elif intent["intent"] == "exit":
        msg = "Shutting down"
        translated = translator.from_english(msg, lang)
        translator.speak(translated, lang)
        return msg

    else:
        msg = "I did not understand"
        translated = translator.from_english(msg, lang)
        translator.speak(translated, lang)
        return msg