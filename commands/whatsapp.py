import subprocess
import time
import pyautogui
import pyperclip


def send_whatsapp_message(contact, message):
    try:
        # OPEN WHATSAPP DESKTOP
        subprocess.Popen("start whatsapp:", shell=True)

        time.sleep(5)

        # SEARCH CONTACT
        pyautogui.hotkey("ctrl", "f")
        time.sleep(1)

        pyperclip.copy(contact)
        pyautogui.hotkey("ctrl", "v")

        time.sleep(2)

        pyautogui.press("enter")

        time.sleep(2)

        # TYPE MESSAGE
        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")

        time.sleep(1)

        pyautogui.press("enter")

        print(f"Message sent to {contact}")

    except Exception as e:
        print("WHATSAPP ERROR:", e)