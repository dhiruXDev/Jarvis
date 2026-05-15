import pyperclip

def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard"
    except Exception as e:
        return f"Error: {e}"

def paste_from_clipboard():
    try:
        text = pyperclip.paste()
        if not text:
            return "Clipboard is empty"
        return text
    except Exception as e:
        return f"Error: {e}"

def clear_clipboard():
    try:
        pyperclip.copy("")
        return "Clipboard cleared"
    except Exception as e:
        return f"Unable to clear clipboard {e}"