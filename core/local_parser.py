import re


def local_parse(command):

    text = command.lower().strip()

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
    if any(word in text for word in [
        "date today",
        "today's date",
        "what is date",
        "current date"
    ]):

        return {
            "intent": "system_control",
            "action": "date"
        }

    # =========================
    # TIME
    # =========================
    if any(word in text for word in [
        "what time",
        "current time",
        "time now"
    ]):

        return {
            "intent": "system_control",
            "action": "time"
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
        app_name = text.replace("maximize ", "").strip()
        return {
            "intent": "system_control",
            "action": "maximize_window",
            "target": app_name
        }

    # =========================
    # SCREENSHOT
    # =========================
    if text == "take screenshot" or text == "capture screen":
        return {
            "intent": "system_control",
            "action": "take_screenshot",
            "filename": "screenshot.png"
        }

    if text.startswith("take screenshot as "):
        filename = text.replace("take screenshot as ", "").strip()
        return {
            "intent": "system_control",
            "action": "take_screenshot",
            "filename": filename
        }

    if text.lower().startswith("play"):
        song_name = text.replace("play", "", 1).strip()
        if song_name:
            return {
                "intent": "play_song",
                "song_name": song_name
            }
    return None