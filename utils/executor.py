from commands.open_app import open_application
from commands.search_web import search_google
from commands.open_website import open_website
from commands.coding import open_potd_leetcode, open_potd_gfg
from commands.system import (
    shutdown_pc,
    restart_pc,
    sleep_pc,
    lock,
    volume,
    check_battery,
    brightness,
)
from commands.whatsapp import send_whatsapp_message

def execute(intent, lang=None):
    print(intent)

    command_type = intent.get("intent")

    # OPEN APP
    if command_type == "open_app":
        target = intent.get("target")
        open_application(target)
        return f"Opening {target}"

    # SEARCH WEB
    elif command_type == "search_web":
        query = intent.get("query")
        search_google(query)
        return f"Searching {query}"

    # OPEN WEBSITE
    elif command_type == "open_website":
        target = intent.get("target")
        open_website(target)
        return f"Opening {target}"

    # POTD
    elif command_type == "open_potd":
        platform = intent.get("platform", "leetcode")
        if platform == "leetcode":
            return open_potd_leetcode()
        elif platform == "gfg":
            return open_potd_gfg()
        else:
            return "Unknown coding platform"

    # SYSTEM CONTROL
    elif command_type == "system_control":
        action = intent.get("action")

        if action == "shutdown":
            shutdown_pc()
            return "Shutting down PC"

        elif action == "restart":
            restart_pc()
            return "Restarting PC"

        elif action == "sleep":
            sleep_pc()
            return "Putting PC to sleep"

        elif action == "lock":
            lock()
            return "Locking PC"

        elif action == "check_battery":
            return check_battery()

    # BRIGHTNESS CONTROL
    elif command_type == "brightness_control":
        level = intent.get("level", 50)
        brightness(level)
        return f"Setting brightness to {level}%"

    # VOLUME CONTROL
    elif command_type == "volume_control":
        level = intent.get("level", 50)
        volume(level)
        return f"Setting volume to {level}%"

    elif command_type == "send_whatsapp_message":
        contact = intent.get("contact")
        message = intent.get("message")
        return send_whatsapp_message(contact, message)
        # if "message" in intent:
        #     return send_whatsapp_message(intent["message"])
        # elif "contact" in intent:
        #     return send_whatsapp_message(intent["contact"])
        # elif "add" in intent:
        #     return AddContact()
        # elif "search" in intent:
        #     return SearchCont(intent["search"])
        # elif "display" in intent:
        #     return Display()
        # # elif "number in contacts" in intent:
        # #     return NameIntheContDataBase(intent["number in contacts"])
    else:
        return "I did not understand the command"