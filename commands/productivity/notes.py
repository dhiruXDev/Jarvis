import subprocess
import pyautogui
# pyrefly: ignore [missing-import]
import pygetwindow as gw
import time


# =========================
# Helper Functions
# =========================

def get_notepad_window():

    windows = [
        w for w in gw.getAllWindows()
        if "Notepad" in w.title or "Untitled" in w.title
    ]

    if windows:
        return windows[0]

    return None

def focus_notepad():

    notepad = get_notepad_window()

    if notepad is None:
        return False

    try:
        notepad.restore()
    except:
        pass

    try:
        notepad.activate()
    except:
        pass

    time.sleep(1)

    return True




# =========================
# Open Notepad
# =========================
def open_notepad():
    try:
        subprocess.Popen("notepad.exe")
        time.sleep(3)
        if get_notepad_window():
            return "Notepad opened successfully"
        return "Failed to open Notepad"
    except Exception as e:
        return f"Error: {e}"


# =========================
# Write New Note
# =========================

def write_note(content):

    try:

        # Open notepad if not already open
        if not get_notepad_window():

            result = open_notepad()

            if "Failed" in result:
                return result

        # Focus window
        if not focus_notepad():
            return "Could not focus Notepad"

        # Clear existing text
        pyautogui.hotkey("ctrl", "a")

        time.sleep(0.3)

        pyautogui.press("backspace")

        time.sleep(0.3)

        # Write content
        pyautogui.write(
            content,
            interval=0.03
        )

        return "Note written successfully"

    except Exception as e:
        return f"Error: {e}"


# =========================
# Append Text
# =========================

def append_note(content):

    try:

        if not get_notepad_window():

            result = open_notepad()

            if "Failed" in result:
                return result

        if not focus_notepad():
            return "Could not focus Notepad"

        # Move to end
        pyautogui.hotkey("ctrl", "end")

        time.sleep(0.3)

        pyautogui.press("enter")

        time.sleep(0.3)

        pyautogui.write(
            content,
            interval=0.03
        )

        return "Content appended successfully"

    except Exception as e:
        return f"Error: {e}"


# =========================
# Save Note
# =========================

def save_note(filename="note.txt"):

    try:

        if not focus_notepad():
            return "Notepad is not open"

        pyautogui.hotkey("ctrl", "s")

        time.sleep(1)

        pyautogui.write(filename)

        time.sleep(0.5)

        pyautogui.press("enter")

        return f"Note saved as {filename}"

    except Exception as e:
        return f"Error: {e}"


# =========================
# Close Notepad
# =========================

def close_notepad():

    try:

        notepad = get_notepad_window()

        if notepad is None:
            return "Notepad is not open"

        notepad.close()

        return "Notepad closed"

    except Exception as e:
        return f"Error: {e}"


# =========================
# Read Current Notepad Text
# (Clipboard-based)
# =========================

def read_notepad():

    try:

        if not focus_notepad():
            return "Notepad is not open"

        pyautogui.hotkey("ctrl", "a")

        time.sleep(0.3)

        pyautogui.hotkey("ctrl", "c")

        time.sleep(0.5)

        import pyperclip

        text = pyperclip.paste()

        return text if text else "Notepad is empty"

    except Exception as e:
        return f"Error: {e}"


# =========================
# Delete All Text
# =========================

def clear_notepad():

    try:

        if not focus_notepad():
            return "Notepad is not open"

        pyautogui.hotkey("ctrl", "a")

        time.sleep(0.3)

        pyautogui.press("backspace")

        return "Notepad cleared"

    except Exception as e:
        return f"Error: {e}"