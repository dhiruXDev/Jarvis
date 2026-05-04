import pywhatkit 

def send_whatsapp_message(phone_number, message):
    try:
        pywhatkit.sendwhatmsg(phone_number, message, 0, 0)
        print("Message sent successfully")
    except:
        print("Failed to send message")

# def whatsapp(command):

#     number = command.get("number")
#     message = command.get("message")

#     if not number or not message:
#         return "Missing phone or message"

#     pywhatkit.sendwhatmsg_instantly(number, message)

#     return "Message sent on WhatsApp"
