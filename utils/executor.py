import ollama
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
    current_date,
    current_time,
    mute_volume,
    unmute_volume,
    keep_quiet, 
    minimize_window,
    close_window,
    maximize_window,
    take_screenshot, 
    delete_file, 
    find_file, 
    open_file
)
from commands.close_app import close_application
from commands.whatsapp import send_whatsapp_message
from commands.play_song import play_song

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

        elif action == "time":
            return current_time()

        elif action == "date":
            return current_date()

        elif action == "mute":
            mute_volume()
            return "Muting volume"

        elif action == "unmute":
            unmute_volume()
            return "Unmuting volume"
        elif action == "minimize_window":
            target = intent.get("target")
            return minimize_window(target)
        elif action == "close_window":
            target = intent.get("target")
            return close_window(target)
        elif action == "maximize_window":
            target = intent.get("target")
            return maximize_window(target)
        elif action == "take_screenshot":
            filename = intent.get("filename", "screenshot.png")
            return take_screenshot(filename)
        elif action == "keep_quiet":
            minutes = intent.get("minutes", 1)
            keep_quiet(minutes)
            return f"Keeping quiet for {minutes} minutes"
        elif action == "open_file":
            filename = intent.get("filename", "")
            return open_file(filename)
        elif action == "delete_file":
            filename = intent.get("filename", "")
            return delete_file(filename)
        elif action == "find_file":
            filename = intent.get("filename", "")
            return find_file(filename)

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
    
    elif command_type == "close_app":
        target = intent.get("target")
        if not target:
            return "No application specified"
        return close_application(target)

    elif command_type == "play_song":
        song_name = intent.get("song_name")
        return play_song(song_name)

        # CHAT
    elif command_type == "chat":
        message = intent.get("message", "")
        return handle_chat(message)

    # UNKNOWN
    else:
        return "I did not understand the command"


def handle_chat(text):
    """
    Handles conversational chatting.
    """

    try:

        response = ollama.chat(
            model='qwen2.5:1.5b',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'You are Jarvis, a smart AI assistant. '
                        'Reply naturally and briefly.'
                    )
                },
                {
                    'role': 'user',
                    'content': text,
                },
            ],
        )

        return response['message']['content']

    except Exception as e:

        print("Chat Error:", e)

        return "Sorry, I cannot chat right now."