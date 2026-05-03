def process(command):
    if "open chrome" in command:
        return {"intent": "open_app", "target": "chrome"}

    elif "open notepad" in command:
        return {"intent": "open_app", "target": "notepad"}

    elif "type" in command:
        return {"intent": "type", "text": command.replace("type", "")}

    elif "exit" in command:
        return {"intent": "exit"}

    return {"intent": "unknown"}