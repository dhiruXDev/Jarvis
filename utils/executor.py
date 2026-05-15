# pyrefly: ignore [missing-import]
from commands.productivity.notes import open_notepad, read_notepad
# pyrefly: ignore [missing-import]
import ollama  

from commands.apps.open_app import open_application
from commands.apps.close_app import close_application
from commands.communication.whatsapp import send_whatsapp_message
from commands.files.file_manager import find_file, open_file, delete_file
from commands.media.play_song import play_song
from commands.web.search_web import search_google
from commands.web.open_website import open_website
from commands.system.power import shutdown_pc, restart_pc, sleep_pc, lock
from commands.system.audio import volume, increase_volume, decrease_volume, mute_volume, unmute_volume, keep_quiet, check_volume
from commands.system.battery import check_battery
from commands.system.brightness import brightness, brightness_up, brightness_down, get_brightness
from commands.system.DateTime import current_date, current_time
from commands.system.windows import minimize_window, maximize_window, close_window
from commands.system.screenshots import take_screenshot, open_screenshot, delete_screenshot
from core.task_manager import task_manager
from modules.agent.worker import handle_agentic_task
from commands.handlers.chat_handler import handle_chat
from commands.productivity.notes import read_notepad, open_notepad, write_note, append_note, save_note, clear_notepad, open_notepad, close_notepad
from commands.networks.bluetooth import show_bluetooth_devices, connect_bluetooth_device, disconnect_bluetooth_device, turn_on_bluetooth, turn_off_bluetooth, get_connected_devices, open_bluetooth_settings
from commands.networks.wifi import turn_on_wifi, turn_off_wifi, show_wifi_password, connect_wifi, show_wifi_networks, connect_wifi_password, show_wifi_settings, disconnect_wifi, check_wifi_status
from commands.networks.hotspot import turn_on_hotspot, turn_off_hotspot, show_hotspot_password, connect_hotspot, open_hotspot_settings, disconnect_hotspot, check_hotspot_status
from commands.networks.internet_speed import check_internet_speed, ping_google
from commands.productivity.clipboard import copy_to_clipboard, paste_from_clipboard, clear_clipboard
from commands.productivity.reminders import set_reminder
# from commands.coding_agent.open_potd import open_leetcode_potd
# from commands.coding_agent.analyze_result import analyze
# from commands.coding_agent.write_code import write_code 
# from commands.coding_agent.extract_problem import extract_problem
# from commands.coding_agent.submit_solution import submit
# from commands.coding_agent.solve_problem import solve_problem

def execute(intent, lang=None):
    print(f"[EXECUTOR] Intent: {intent}")
    
    command_type = intent.get("intent")
    action = intent.get("action")

    # =========================
    # AUDIO
    # =========================
    if command_type == "audio":
        if action == "set":
            level = intent.get("level", 50)
            volume(level)
            return f"Setting volume to {level}%"
        elif action == "increase":
            success = increase_volume()
            if success:
                return "Volume increased"
            return "Unable to increase volume. Maximum volume is reached."
        elif action == "decrease":
            success = decrease_volume()
            if success:
                return "Volume decreased"
            return "Unable to decrease volume. Minimum volume is reached."
        elif action == "mute":
            mute_volume()
            return "Volume muted"
        elif action == "unmute":
            unmute_volume()
            return "Volume unmuted"
        elif action == "get":
            vol = check_volume()
            return f"Volume is at {vol}%" if vol else "Unable to check volume"
        elif action == "keep_quiet":
            minutes = intent.get("minutes", 1)
            keep_quiet(minutes)
            return f"Keeping quiet for {minutes} minutes"

    # =========================
    # BRIGHTNESS
    # =========================
    elif command_type == "brightness":
        if action == "set":
            level = intent.get("level", 50)
            brightness(level)
            return f"Setting brightness to {level}%"
        elif action == "increase":
            brightness_up()
            return "Brightness increased"
        elif action == "decrease":
            brightness_down()
            return "Brightness decreased"
        elif action == "get":
            return get_brightness()

    # =========================
    # SYSTEM POWER
    # =========================
    elif command_type == "system_power":
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

    # =========================
    # SYSTEM INFO
    # =========================
    elif command_type == "system_info":
        if action == "battery":
            return check_battery()
        elif action == "time":
            return current_time()
        elif action == "date":
            return current_date()

    # =========================
    # WINDOW
    # =========================
    elif command_type == "window":
        target = intent.get("target", "")
        if action == "minimize":
            return minimize_window(target)
        elif action == "maximize":
            return maximize_window(target)
        elif action == "close":
            return close_window(target)

    # =========================
    # FILE MANAGER
    # =========================
    elif command_type == "file":
        filename = intent.get("filename", "")
        if action == "find":
            return find_file(filename)
        elif action == "open":
            return open_file(filename)
        elif action == "delete":
            return delete_file(filename)

    # =========================
    # SCREENSHOT
    # =========================
    elif command_type == "screenshot":
        filename = intent.get("filename", "screenshot.png")
        if action == "take":
            return take_screenshot(filename)
        elif action == "open":
            return open_screenshot(filename)
        elif action == "delete":
            return delete_screenshot(filename)

    # =========================
    # APP
    # =========================
    elif command_type == "app":
        target = intent.get("target")
        if action == "open":
            open_application(target)
            return f"Opening {target}"
        elif action == "close":
            if not target: return "No application specified"
            return close_application(target)

    # =========================
    # WEB
    # =========================
    elif command_type == "web":
        if action == "search":
            query = intent.get("query")
            search_google(query)
            return f"Searching {query}"
        elif action == "open_website":
            target = intent.get("target")
            open_website(target)
            return f"Opening {target}"

    # =========================
    # MEDIA
    # =========================
    elif command_type == "media":
        if action == "play_song":
            song_name = intent.get("song_name")
            return play_song(song_name)

    # =========================
    # COMMUNICATION
    # =========================
    elif command_type == "communication":
        if action == "whatsapp":
            contact = intent.get("contact")
            message = intent.get("message")
            return send_whatsapp_message(contact, message)

    # =========================
    # AGENTIC TASK
    # =========================
    elif command_type == "agentic":
        message = intent.get("message", "")
        task_manager.run_task(lambda: handle_agentic_task(message))
        return "I have delegated this heavy task to my background worker."

    # =========================
    # CHAT
    # =========================
    elif command_type == "chat":
        message = intent.get("message", "")
        return handle_chat(message)

    # =========================
    # BLUETOOTH
    # =========================
    elif command_type == "bluetooth":
        if action in ("show", "show_devices"):
            return show_bluetooth_devices()
        elif action in ("settings", "open_settings"): 
            return open_bluetooth_settings()
        elif action in ("connect", "connect_device"):
            return connect_bluetooth_device(intent.get("device_name", ""))
        elif action == "turn_on":
            return turn_on_bluetooth()
        elif action == "turn_off":
            return turn_off_bluetooth()
        elif action in ("disconnect", "disconnect_device"):
            return disconnect_bluetooth_device(intent.get("device_name", ""))
        elif action == "get_connected_devices":
            return get_connected_devices()

    # =========================
    # NOTES
    # =========================
    elif command_type == "note":
        if action == "open":
            return open_notepad()
        elif action == "write":
            return write_note(intent.get("content", ""))
        elif action == "append":
            return append_note(intent.get("content", ""))
        elif action == "save":
            return save_note(intent.get("filename", "note.txt"))
        elif action == "read":
            return read_notepad()
        elif action == "clear":
            return clear_notepad()
        elif action == "close":
            return close_notepad()

    # =========================
    # WIFI
    # =========================
    elif command_type == "wifi":
        if action == "turn_on":
            return turn_on_wifi()
        elif action == "turn_off":
            return turn_off_wifi()
        elif action == "show_password":
            return show_wifi_password()
        elif action == "connect":
            return connect_wifi(intent.get("ssid", ""))
        elif action == "show_networks":
            return show_wifi_networks()
        elif action == "connect_password":
            return connect_wifi_password(intent.get("ssid", ""), intent.get("password", ""))
        elif action == "open_settings":
            return show_wifi_settings()
        elif action == "disconnect":
            return disconnect_wifi()
        elif action == "check_status":
            return check_wifi_status()

    # =========================
    # INTERNET SPEED TEST 
    # =========================
    elif command_type == "internet_speed":
        if action in ("check", "check_speed"):
            return check_internet_speed()
        elif action == "ping":
            return ping_google()

    # =========================
    # HOTSPOT
    # =========================
    elif command_type == "hotspot":
        if action in ("on", "turn_on"):
            return turn_on_hotspot()
        elif action in ("off", "turn_off"):
            return turn_off_hotspot()
        elif action == "show_password":
            return show_hotspot_password()
        elif action in ("settings", "open_settings"):
            return open_hotspot_settings()
        elif action == "check_status":
            return check_hotspot_status()
        elif action == "disconnect":
            return disconnect_hotspot()
        elif action == "connect":
            return connect_hotspot(intent.get("ssid", ""), intent.get("password", ""))


    # =========================
    # CLIPBOARD
    # =========================
    elif command_type == "clipboard":
        if action == "copy":
            return copy_to_clipboard(intent.get("text", ""))
        elif action == "paste":
            return paste_from_clipboard()
        elif action == "clear":
            return clear_clipboard()   

    # =========================
    # REMINDER
    # =========================
    elif command_type == "reminder":
        if action == "set":
            return set_reminder(intent.get("message", ""), intent.get("seconds", 0))

    # =========================
    # CODING
    # =========================
    # elif command_type == "leetcode":
    #     if action == "potd":
    #         page, browser, playwright = open_leetcode_potd()
    #         problem = extract_problem(page)
    #         if not problem:
    #             return "Failed to extract problem from LeetCode"
    #         code = solve_problem(problem["description"])
    #         success = write_code(page, code)
    #         if not success:
    #             return "Failed to write code"
    #         submit_success = submit(page)
    #         if not submit_success:
    #             return "Failed to submit code"
    #         result = analyze(page)
    #         return result


    # =========================
    # SYSTEM EXIT / UNKNOWN
    # =========================
    elif command_type == "system" and action == "exit":
        return "Goodbye"
        
    return "I did not understand the command"