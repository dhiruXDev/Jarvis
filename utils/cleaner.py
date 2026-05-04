def clean_command(command):
    command = command.strip()
    command = command.lower()
    if "hello" in command:
        command = command.replace("hello", "")
    if "jarvis" in command:
        command = command.replace("jarvis", "")
    return command  