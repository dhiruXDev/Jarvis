import re

def local_parse(command):
    text = command.lower().strip()
    FILLER_WORDS = [
        "jarvis", "please", "can you", "could you", "would you", "for me"
    ]
    for word in FILLER_WORDS:
        text = text.replace(word, "")
    # Keep alphanumeric, spaces, and dots (for file extensions)
    text = re.sub(r"[^\w\s\.]", "", text)
    text = " ".join(text.split())

    # =========================
    # FILE MANAGER
    # =========================
    if text.startswith("find file "):
        return {"intent": "file", "action": "find", "filename": text.replace("find file ", "").strip()}
    if text.startswith("find "):
        return {"intent": "file", "action": "find", "filename": text.replace("find ", "").strip()}
    if text.startswith("open file "):
        return {"intent": "file", "action": "open", "filename": text.replace("open file ", "").strip()}
    if text.startswith("delete file "):
        return {"intent": "file", "action": "delete", "filename": text.replace("delete file ", "").strip()}

    # =========================
    # OPEN WEBSITES
    # =========================
    websites = ["youtube", "github", "gmail", "leetcode", "chatgpt", "facebook", "instagram", "twitter"]
    for site in websites:
        if text == site or text == f"open {site}":
            return {"intent": "web", "action": "open_website", "target": site}

    # =========================
    # PLAY SONG / YOUTUBE SEARCH
    # =========================
    if text.startswith("play "):
        return {"intent": "media", "action": "play_song", "song_name": text.replace("play ", "").strip()}
    if "youtube" in text and ("open " in text or "search " in text or "play " in text):
        query = text.replace("open ", "").replace("search ", "").replace("play ", "").replace("youtube", "").replace(" on ", " ").replace(" pe ", " ").strip()
        if query and query != "youtube":
            return {"intent": "media", "action": "play_song", "song_name": query}

    # =========================
    # OPEN APP
    # =========================
    if text.startswith("open "):
        return {"intent": "app", "action": "open", "target": text.replace("open ", "").strip()}

    # =========================
    # CLOSE APP
    # =========================
    if text.startswith("close "):
        return {"intent": "app", "action": "close", "target": text.replace("close ", "").strip()}

    # =========================
    # SEARCH WEB
    # =========================
    if text.startswith("search ") or text.startswith("google "):
        query = text.replace("search ", "").replace("google ", "").strip()
        return {"intent": "web", "action": "search", "query": query}

    # =========================
    # AUDIO
    # =========================
    volume_match = re.search(r"volume (\d+)", text)
    if volume_match:
        return {"intent": "audio", "action": "set", "level": int(volume_match.group(1))}
    if text in ["increase volume", "volume up", "make it louder"]:
        return {"intent": "audio", "action": "increase"}
    if text in ["decrease volume", "volume down", "make it quieter"]:
        return {"intent": "audio", "action": "decrease"}
    if re.search(r"\bunmute\b", text):
        return {"intent": "audio", "action": "unmute"}
    if re.search(r"\bmute\b", text):
        return {"intent": "audio", "action": "mute"}
    if text in ["what is the volume", "check volume", "what is my volume"]:
        return {"intent": "audio", "action": "get"}
    if text in ["keep quiet", "be quiet", "quiet"]:
        return {"intent": "audio", "action": "keep_quiet", "minutes": 1}
    quiet_match = re.search(r"quiet for (\d+)", text)
    if quiet_match:
        return {"intent": "audio", "action": "keep_quiet", "minutes": int(quiet_match.group(1))}

    # =========================
    # BRIGHTNESS
    # =========================
    brightness_match = re.search(r"brightness (\d+)", text)
    if brightness_match:
        return {"intent": "brightness", "action": "set", "level": int(brightness_match.group(1))}
    if text in ["increase brightness", "brightness up", "make it brighter"]:
        return {"intent": "brightness", "action": "increase"}
    if text in ["decrease brightness", "brightness down", "make it dimmer"]:
        return {"intent": "brightness", "action": "decrease"}
    if text in ["what is the brightness", "check brightness", "what is my brightness", "get brightness"]:
        return {"intent": "brightness", "action": "get"}

    # =========================
    # SYSTEM POWER
    # =========================
    if any(word in text for word in ["shutdown", "shut down", "power off"]):
        return {"intent": "system_power", "action": "shutdown"}
    if any(word in text for word in ["restart", "reboot"]):
        return {"intent": "system_power", "action": "restart"}
    if any(word in text for word in ["sleep pc", "sleep computer", "hibernate"]):
        return {"intent": "system_power", "action": "sleep"}
    if any(word in text for word in ["lock pc","lock my pc", "lock computer", "lock system"]):
        return {"intent": "system_power", "action": "lock"}

    # =========================
    # SYSTEM INFO
    # =========================
    if "battery" in text:
        return {"intent": "system_info", "action": "battery"}
    if "time" in text:
        return {"intent": "system_info", "action": "time"}
    if "date" in text:
        return {"intent": "system_info", "action": "date"}

    # =========================
    # WINDOW MANAGER
    # =========================
    if text.startswith("minimize "):
        return {"intent": "window", "action": "minimize", "target": text.replace("minimize ", "").replace("window", "").strip()}
    if text.startswith("close window "):
        return {"intent": "window", "action": "close", "target": text.replace("close window ", "").strip()}
    if text.startswith("maximize "):
        return {"intent": "window", "action": "maximize", "target": text.replace("maximize", "").replace("window", "").strip()}

    # =========================
    # SCREENSHOT
    # =========================
    if text in ["take screenshot", "capture screen"]:
        return {"intent": "screenshot", "action": "take", "filename": "screenshot.png"}
    match = re.search(r"(take screenshot|capture screen)( and save as| as)? (.+)", text)
    if match:
        filename = match.group(3).strip()
        if not filename.endswith(".png"): filename += ".png"
        return {"intent": "screenshot", "action": "take", "filename": filename}

    # =========================
    # WHATSAPP
    # =========================
    if "whatsapp" in text or text.startswith("send "):
        cleaned = text.replace("send", "").replace("whatsapp", "").replace("message", "").strip()
        parts = cleaned.split()
        if len(parts) >= 2:
            return {"intent": "communication", "action": "whatsapp", "contact": parts[0], "message": " ".join(parts[1:])}

    # =========================
    # EXIT
    # =========================
    if text in ["exit", "quit", "stop jarvis", "goodbye"]:
        return {"intent": "system", "action": "exit"}

    # =========================
    # AGENTIC TASK
    # =========================
    heavy_keywords = ["research ", "analyze ", "write a report", "write a script", "write code", "deep dive", "summarize ", "write an essay", "create a plan", "agent ", "run task "]
    if any(text.startswith(kw) or kw in text for kw in heavy_keywords):
        return {"intent": "agentic", "action": "task", "message": command}

    return None