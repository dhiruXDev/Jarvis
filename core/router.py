from commands.open_app import open_application
from commands.search_web import search_google
from commands.whatsapp import send_whatsapp_message
from commands.coding import leetcode_open_potd, gfg_open_potd

def route_command(command):
    if command["intent"] == "open_application":
        open_application(command)
    elif command["intent"] == "search_web":
        search_google(command)
    elif command["intent"] == "whatsapp":
        whatsapp(command)
    elif command["intent"] == "coding":
        coding(command)
    elif command["intent"] == "system":
        system(command)
    else:
        print("Command not recognized ")