import subprocess
import time
import pyautogui
import pyperclip


def send_whatsapp_message(contact, message):
    try:
        # Open WhatsApp Desktop
        subprocess.Popen("start whatsapp:", shell=True)
        time.sleep(5)
        # Open search
        pyautogui.hotkey("ctrl", "f")
        time.sleep(1)
        # Paste contact name
        pyperclip.copy(contact)

        pyautogui.hotkey("ctrl", "v")

        time.sleep(2)

        # Open chat
        pyautogui.press("enter")

        time.sleep(1)

        # Paste message
        pyperclip.copy(message)

        pyautogui.hotkey("ctrl", "v")

        time.sleep(1)

        # Send message
        pyautogui.press("enter")

        return f"Message sent to {contact}"

    except Exception as e:

        return f"WhatsApp automation failed: {str(e)}"