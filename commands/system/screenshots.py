import pyautogui
import time
import os
from pathlib import Path
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def take_screenshot(filename="screenshot.png"):
    try:
        if not filename.endswith(".png"):
            filename += ".png"
        save_path = SCREENSHOT_DIR / filename
        print(f"[SCREENSHOT] Saving to: {save_path}")
        time.sleep(1)
        screenshot = pyautogui.screenshot()
        print("[SCREENSHOT] Screenshot captured")
        screenshot.save(save_path)
        print("[SCREENSHOT] Screenshot saved successfully")
        return f"Screenshot saved as {save_path}"
    except Exception as e:
        print(f"[SCREENSHOT ERROR] {e}")
        return "Unable to take screenshot"

def open_screenshot(filename):
    try:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            os.startfile(file_path)
            return f"Opened {filename}"
        else:
            return f"File '{filename}' not found"
    except Exception as e:
        print(f"Open screenshot error: {e}")
        return "Unable to open screenshot"

def delete_screenshot(filename):
    try:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"Deleted {filename}"
        else:
            return f"File '{filename}' not found"
    except Exception as e:
        print(f"Delete screenshot error: {e}")
        return "Unable to delete screenshot"

