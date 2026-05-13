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
from commands.coding import open_potd_leetcode, open_potd_gfg
from core.task_manager import task_manager
from modules.agent.worker import handle_agentic_task
from commands.handlers.chat_handler import handle_chat


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
    # SYSTEM EXIT / UNKNOWN
    # =========================
    elif command_type == "system" and action == "exit":
        return "Goodbye"
        
    return "I did not understand the command"