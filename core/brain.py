# def process(command):
#     if "open chrome" in command:
#         return {"intent": "open_app", "target": "chrome"}

#     elif "open notepad" in command:
#         return {"intent": "open_app", "target": "notepad"}

#     elif "type" in command:
#         return {"intent": "type", "text": command.replace("type", "")}

#     elif "exit" in command:
#         return {"intent": "exit"}

#     return {"intent": "unknown"}

def process(command):
    command = command.lower()

    if "notepad" in command:
        return {"intent": "open_app", "target": "notepad"}

    elif "chrome" in command:
        return {"intent": "open_app", "target": "chrome"}

    elif "type" in command:
        text = command.replace("type", "").strip()
        return {"intent": "type", "text": text}

    elif "exit" in command or "stop" in command:
        return {"intent": "exit"}

    return {"intent": "unknown"}