import re

def local_parse(command):
    text = command.lower().strip()
    FILLER_WORDS = [
    "jarvis",
    "please",
    "can you",
    "could you",
    "would you",
    "for me"
]
    for word in FILLER_WORDS:
        text = text.replace(word, "")
    text = re.sub(r"[^\w\s]", "", text)
    text = " ".join(text.split())

     # =========================
    # File Manager
    # =========================
    if text.startswith("find "):
        filename = text.replace("find ", "").strip()
        return {
            "intent": "find_file",
            "filename": filename
        }

    if text.startswith("open file "):
        filename = text.replace("open file ", "").strip()
        return {
            "intent": "open_file",
            "filename": filename
        }

    if text.startswith("delete file "):
        filename = text.replace("delete file ", "").strip()
        return {
            "intent": "delete_file",
            "filename": filename
        }
    # =========================
    # OPEN APP
    # =========================
    if text.startswith("open "):

        app = text.replace("open ", "").strip()

        return {
            "intent": "open_app",
            "target": app
        }

    # =========================
    # CLOSE APP
    # =========================
    if text.startswith("close "):
        app = text.replace("close ", "").strip()
        return {
            "intent": "close_app",
            "target": app
        }

    # =========================
    # SEARCH WEB
    # =========================
    if text.startswith("search "):
        query = text.replace("search ", "").strip()
        return {
            "intent": "search_web",
            "query": query
        }

    if text.startswith("google "):
        query = text.replace("google ", "").strip()
        return {
            "intent": "search_web",
            "query": query
        }

    # =========================
    # OPEN WEBSITES
    # =========================
    websites = [
        "youtube",
        "github",
        "gmail",
        "leetcode",
        "chatgpt",
        "facebook",
        "instagram",
        "twitter"
    ]

    for site in websites:
        if text == site or text == f"open {site}":
            return {
                "intent": "open_website",
                "target": site
            }

    # =========================
    # VOLUME CONTROL
    # =========================
    volume_match = re.search(
        r"volume (\d+)",
        text
    )

    if volume_match:

        return {
            "intent": "volume_control",
            "level": int(volume_match.group(1))
        }

    # =========================
    # BRIGHTNESS CONTROL
    # =========================
    brightness_match = re.search(
        r"brightness (\d+)",
        text
    )

    if brightness_match:

        return {
            "intent": "brightness_control",
            "level": int(brightness_match.group(1))
        }

    # =========================
    # SHUTDOWN
    # =========================
    if any(word in text for word in [
        "shutdown",
        "shut down",
        "power off"
    ]):

        return {
            "intent": "system_control",
            "action": "shutdown"
        }

    # =========================
    # RESTART
    # =========================
    if any(word in text for word in [
        "restart",
        "reboot"
    ]):

        return {
            "intent": "system_control",
            "action": "restart"
        }

    # =========================
    # SLEEP
    # =========================
    if any(word in text for word in [
        "sleep pc",
        "sleep computer",
        "hibernate"
    ]):

        return {
            "intent": "system_control",
            "action": "sleep"
        }

    # =========================
    # LOCK
    # =========================
    if any(word in text for word in [
        "lock pc",
        "lock computer",
        "lock system"
    ]):

        return {
            "intent": "system_control",
            "action": "lock"
        }

    # =========================
    # BATTERY
    # =========================
    if "battery" in text:

        return {
            "intent": "system_control",
            "action": "check_battery"
        }

    # =========================
    # DATE
    # =========================
    if "time" in text:
        return {
            "intent": "system_control",
            "action": "time"
        }

    # =========================
    # DATE
    # =========================
    if "date" in text:
        return {
            "intent": "system_control",
            "action": "date"
        }

    # =========================
    # MUTE
    # =========================
    if any(word in text for word in [
        "mute",
        "mute volume",
        "silent"
    ]):

        return {
            "intent": "system_control",
            "action": "mute"
        }

    # =========================
    # UNMUTE
    # =========================
    if any(word in text for word in [
        "unmute",
        "sound on"
    ]):

        return {
            "intent": "system_control",
            "action": "unmute"
        }

    # =========================
    # KEEP QUIET
    # =========================
    quiet_match = re.search(
        r"quiet for (\d+)",
        text
    )

    if quiet_match:

        return {
            "intent": "system_control",
            "action": "keep_quiet",
            "minutes": int(quiet_match.group(1))
        }

    # =========================
    # POTD
    # =========================
    if any(word in text for word in [
        "potd",
        "problem of the day",
        "daily coding problem"
    ]):

        return {
            "intent": "open_potd"
        }

    # =========================
    # EXIT
    # =========================
    if text in [
        "exit",
        "quit",
        "stop jarvis",
        "goodbye"
    ]:

        return {
            "intent": "exit"
        }
    
    # =========================
    # MINIMIZE WINDOW
    # =========================
    if text.startswith("minimize "):
        app_name = text.replace("minimize ", "").strip()
        app_name = app_name.replace("window", "").strip()
        return {
            "intent": "system_control",
            "action": "minimize_window",
            "target": app_name
        }

    # =========================
    # CLOSE WINDOW
    # =========================
    if text.startswith("close window "):
        app_name = text.replace("close window ", "").strip()
        return {
            "intent": "system_control",
            "action": "close_window",
            "target": app_name
        }

    # =========================
    # MAXIMIZE WINDOW
    # =========================
    if text.startswith("maximize "):
        app_name = text.replace("maximize", "").strip()
        app_name = app_name.replace("window", "").strip()
        return {
            "intent": "system_control",
            "action": "maximize_window",
            "target": app_name
        }

    # # =========================
    # # SCREENSHOT
    # # =========================
    if text in ["take screenshot", "capture screen"]:
        return {
            "intent": "system_control",
            "action": "take_screenshot",
            "filename": "screenshot.png"
        }

    match = re.search(
        r"(take screenshot|capture screen)( and save as| as)? (.+)",
        text
    )

    if match:
        filename = match.group(3).strip()

        if not filename.endswith(".png"):
            filename += ".png"

        return {
            "intent": "system_control",
            "action": "take_screenshot",
            "filename": filename
        }
        
    # =========================
    # WHATSAPP MESSAGE
    # =========================
    
    if "whatsapp" in text or text.startswith("send "):

        cleaned = text

        cleaned = cleaned.replace("send", "")
        cleaned = cleaned.replace("whatsapp", "")
        cleaned = cleaned.replace("message", "")

        cleaned = cleaned.strip()

        parts = cleaned.split()

        if len(parts) >= 2:

            contact = parts[0]

            message = " ".join(parts[1:])

            return {
                "intent": "send_whatsapp_message",
                "contact": contact,
                "message": message
            }

    # =========================
    # AGENTIC / HEAVY TASK
    # =========================
    heavy_keywords = [
        "research ", "analyze ", "write a report", "write a script",
        "write code", "deep dive", "summarize ",
        "write an essay", "create a plan", "agent ", "run task "
    ]
    if any(text.startswith(kw) or kw in text for kw in heavy_keywords):
        return {
            "intent": "agentic_task",
            "message": command  # Use the original command for full context
        }

    return None

   