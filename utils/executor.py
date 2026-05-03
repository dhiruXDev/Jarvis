from actions import system, typing

def execute(intent):
    if intent["intent"] == "open_app":
        system.open_app(intent["target"])

    elif intent["intent"] == "type":
        typing.type_text(intent["text"])

    elif intent["intent"] == "exit":
        return False

    else:
        print("Unknown command")

    return True