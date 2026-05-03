 
# from core.speaker import speak
# import actions.system as system
# import actions.typing as typing

# def execute(intent):
#     if intent["intent"] == "open_app":
#         speak(f"Opening {intent['target']}")
#         system.open_app(intent["target"])

#     elif intent["intent"] == "type":
#         speak("Typing now")
#         typing.type_text(intent["text"])

#     elif intent["intent"] == "exit":
#         return False

#     else:
#         speak("I did not understand")

#     return True
from core.speaker import speak
import actions.system as system
import actions.typing as typing

def execute(intent):
    if intent["intent"] == "open_app":
        speak(f"Opening {intent['target']}")
        system.open_app(intent["target"])

    elif intent["intent"] == "type":
        speak("Typing now")
        typing.type_text(intent["text"])

    elif intent["intent"] == "exit":
        speak("Shutting down")
        return False

    else:
        speak("I did not understand")

    return True