from commands.open_app import open_application
from commands.search_web import search_google
from commands.whatsapp import send_whatsapp_message
from commands.coding import open_potd_leetcode, open_potd_gfg 
from commands.system import shutdown_pc, restart_pc, sleep_pc, lock, check_battery, brightness, volume, current_date, current_time, mute_volume, unmute_volume, keep_quiet
from commands.close_app import close_application

def route_command(command):
    if command["intent"] == "whatsapp": 
        if "message" in command and "contact" in command:
            return send_whatsapp_message(command["contact"], command["message"])
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
        elif "time" in command:
            return current_time()
        elif "date" in command:
            return current_date()
        elif "mute" in command:
            return mute_volume()
        elif "unmute" in command:
            return unmute_volume()
        elif "keep quiet" in command:
            return keep_quiet(command["minutes"])
    elif command["intent"] == "close_app":
        target = command.get("target")
        return close_application(target)
    else:
        print("Command not recognized ")