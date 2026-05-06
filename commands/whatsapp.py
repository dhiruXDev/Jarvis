# import pywhatkit 

# def send_whatsapp_message(phone_number, message):
#     try:
#         pywhatkit.sendwhatmsg(phone_number, message, 0, 0)
#         print("Message sent successfully")
#     except:
#         print("Failed to send message")

# # def whatsapp(command):

# #     number = command.get("number")
# #     message = command.get("message")

# #     if not number or not message:
# #         return "Missing phone or message"

# #     pywhatkit.sendwhatmsg_instantly(number, message)

# #     return "Message sent on WhatsApp"
from playwright.sync_api import sync_playwright
import time

# Persistent browser session
USER_DATA_DIR = "playwright_whatsapp_session"


def send_whatsapp_message(contact_name, message):

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=False
            )

            page = browser.new_page()

            print("Opening WhatsApp Web...")

            page.goto("https://web.whatsapp.com")

            print("Waiting for WhatsApp to load...")
            page.wait_for_timeout(10000)

            # Search box
            search_box = page.locator('div[contenteditable="true"]').nth(0)

            search_box.click()

            search_box.fill(contact_name)

            page.wait_for_timeout(3000)

            # Click contact
            page.locator(f'text="{contact_name}"').click()

            page.wait_for_timeout(2000)

            # Message box
            message_box = page.locator('div[contenteditable="true"]').nth(1)

            message_box.click()

            message_box.fill(message)

            page.keyboard.press("Enter")

            print(f"Message sent to {contact_name}")

            page.wait_for_timeout(3000)

            browser.close()

            return True

    except Exception as e:

        print(f"WhatsApp Error: {e}")

        return False