from commands.open_app import open_application
from commands.search_web import search_google
from commands.whatsapp import send_whatsapp_message
from commands.coding import open_potd_leetcode, open_potd_gfg 
from commands.system import shutdown_pc, restart_pc, sleep_pc, lock, check_battery, brightness, volume
def route_command(command):
    if command["intent"] == "whatsapp": 
        if "message" in command and "contact" in command:
            return send_whatsapp_message(command["contact"], command["message"])
        # elif "contact" in command:
        #     return send_whatsapp_message(command["contact"])
        # elif "add" in command:    
        #     return AddContact()
        # elif "search" in command:
        #     return SearchCont(command["search"])
        # elif "display" in command:
        #     return Display()
        # elif "number in contacts" in command:
        #     return NameIntheContDataBase(command["number in contacts"])
    if command["intent"] == "open_application":
        open_application(command)
    elif command["intent"] == "search_web":
        search_google(command)
    elif command["intent"] == "coding":
        if "leetcode" in command:
            return open_potd_leetcode()
        elif "gfg" in command:
            return open_potd_gfg()
        
    elif command["intent"] == "system":
        if "shutdown" in command:
            return shutdown_pc()
        elif "restart" in command:
            return restart_pc()
        elif "sleep" in command:
            return sleep_pc()
        elif "lock" in command:
            return lock()
        elif "check battery" in command:
            return check_battery()
        elif "brightness" in command:
            return brightness(command["brightness"])
        elif "volume" in command:
            return volume(command["volume"])
    else:
        print("Command not recognized ")