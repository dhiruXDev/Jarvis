from ast import Return
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
    # FILE MANAGER - FOLDERS OPEN
    # =========================
    if text.startswith("open downloads"):
        return {"intent": "file", "action": "open_downloads"}
    if text.startswith("open desktop"):
        return {"intent": "file", "action": "open_desktop"}
    if text.startswith("open documents"):
        return {"intent": "file", "action": "open_documents"}
    if text.startswith("open drives"):
        return {"intent": "file", "action": "open_drives"}
    if text.startswith("open folder "):
        return {"intent": "file", "action": "open_folder", "folder_name": text.replace("open folder ", "").strip()}
    
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
    # BLUETOOTH
    # =========================
    if "bluetooth" in text:
        if "show" in text:
            return {"intent": "bluetooth", "action": "show_devices"}
        if "settings" in text:
            return {"intent": "bluetooth", "action": "open_settings"}
        if "disconnect" in text:
            return {"intent": "bluetooth", "action": "disconnect_device", "device_name": text.replace("disconnect bluetooth device", "").replace("disconnect", "").replace("bluetooth", "").strip()}
        if "connected" in text:
            return {"intent": "bluetooth", "action": "get_connected_devices"}
        if "connect" in text:
            return {"intent": "bluetooth", "action": "connect_device", "device_name": text.replace("connect bluetooth device", "").replace("connect", "").replace("bluetooth", "").strip()}
        if "off" in text.split() or "disable" in text:
            return {"intent": "bluetooth", "action": "turn_off"}
        if "on" in text.split() or "enable" in text:
            return {"intent": "bluetooth", "action": "turn_on"}

    # =========================
    # WIFI
    # =========================
    if "wifi" in text:
        if "off" in text.split() or "disable" in text:
            return {"intent": "wifi", "action": "turn_off"}
        if "on" in text.split() or "enable" in text:
            return {"intent": "wifi", "action": "turn_on"}
        if "password" in text:
            if "connect" in text:
                return {"intent": "wifi", "action": "connect_password", "ssid": text.replace("connect to wifi", "").replace("connect", "").replace("password", "").replace("wifi", "").strip()}
            return {"intent": "wifi", "action": "show_password"}
        if "networks" in text or "available" in text:
            return {"intent": "wifi", "action": "show_networks"}
        if "settings" in text:
            return {"intent": "wifi", "action": "open_settings"}
        if "disconnect" in text:
            return {"intent": "wifi", "action": "disconnect"}
        if "status" in text:
            return {"intent": "wifi", "action": "check_status"}
        if "connect" in text:
            return {"intent": "wifi", "action": "connect", "ssid": text.replace("connect to wifi", "").replace("connect", "").replace("wifi", "").strip()}

    # =========================
    # HOTSPOT
    # =========================
    if "hotspot" in text:
        if "on" in text.split() or "enable" in text:
            return {"intent": "hotspot", "action": "turn_on"}
        if "off" in text.split() or "disable" in text:
            return {"intent": "hotspot", "action": "turn_off"}
        if "password" in text:
            return {"intent": "hotspot", "action": "show_password"}
        if "settings" in text:
            return {"intent": "hotspot", "action": "open_settings"}
        if "disconnect" in text:
            return {"intent": "hotspot", "action": "disconnect"}
        if "status" in text:
            return {"intent": "hotspot", "action": "check_status"}
        if "connect" in text:
            return {"intent": "hotspot", "action": "connect", "ssid": text.replace("connect to hotspot", "").replace("connect", "").replace("hotspot", "").strip()}

    # =========================
    # NOTES 
    # =========================
    if "note" in text:
        if "open" in text:
            return {"intent": "note", "action": "open"}
        elif "write" in text or "type" in text:
            content = text.replace("write on notepad", "").replace("write in notepad", "").replace("write note", "").replace("write", "").replace("type on notepad", "").replace("type in notepad", "").replace("type note", "").replace("type", "").strip()
            return {"intent": "note", "action": "write", "content": content}
        elif "add" in text or "append" in text:
            content = text.replace("add to notepad", "").replace("add to note", "").replace("add note", "").replace("append to notepad", "").replace("append note", "").replace("add", "").replace("append", "").strip()
            return {"intent": "note", "action": "append", "content": content}
        elif "save" in text:
            filename = text.replace("save note as", "").replace("save note", "").replace("save", "").strip()
            return {"intent": "note", "action": "save", "filename": filename if filename else "note.txt"}
        elif "read" in text:
            return {"intent": "note", "action": "read"}
        elif "clear" in text:
            return {"intent": "note", "action": "clear"}
        elif "close" in text:
            return {"intent": "note", "action": "close"}

    # =========================
    # CODING ON LEETCODE 
    # =========================
    if "leetcode" in text or "potd" in text or "problem of the day" in text:
        if "open" in text and ("potd" in text or "problem of the day" in text):
            return {"intent": "leetcode", "action": "open_potd"}
        if "solve" in text and ("potd" in text or "problem of the day" in text):
            return {"intent": "leetcode", "action": "solve_potd"}
        if "potd" in text or "problem of the day" in text or "problem of day" in text: 
            return {"intent": "leetcode", "action": "open_potd"} 
        if "write code" in text:
            return {"intent": "leetcode", "action": "write_code"}
        if "analyze result" in text:
            return {"intent": "leetcode", "action": "analyze_result"}
        if "extract problem" in text:
            return {"intent": "leetcode", "action": "extract_problem"}
        if "submit solution" in text:
            return {"intent": "leetcode", "action": "submit_solution"}
        if "solve problem" in text:
            return {"intent": "leetcode", "action": "solve_problem"}

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
    # INTERNET SPEED
    # =========================
    if "internet" in text and "speed" in text:
        return {"intent": "internet_speed", "action": "check_speed"}
    if "ping" in text and "google" in text:
        return {"intent": "internet_speed", "action": "ping_google"}
    if text.startswith("check internet speed"):
        return {"intent": "internet_speed", "action": "check_speed"}
    if text.startswith("ping google"):
        return {"intent": "internet_speed", "action": "ping_google"}



    # =========================
    # CLIPBOARD
    # =========================
    if "copy " in text:
        return {"intent": "clipboard", "action": "copy", "text": text.replace("copy ", "").strip()}
    if "paste" in text or "paset" in text or "paste it" in text or "paste this" in text or "past text" in text:
        return {"intent": "clipboard", "action": "paste"}
    if "clear clipboard" in text or "copy clear" in text or "clear clip" in text or "clipboard clear" in text:
        return {"intent": "clipboard", "action": "clear"}

    # =========================
    # REMINDER / ALARM / TIMER
    # =========================
    if any(k in text for k in ["remind", "alarm", "timer"]):
        # Match time patterns like "in 5 minutes", "after 10 seconds", "for 1 hour"
        time_match = re.search(r"\b(in|after|for)\s+(\d+)\s*(minute|min|second|sec|hour|hr)s?\b", text)
        if time_match:
            val = int(time_match.group(2))
            unit = time_match.group(3).lower()
            seconds = 0
            if "hour" in unit or "hr" in unit:
                seconds = val * 3600
            elif "minute" in unit or "min" in unit:
                seconds = val * 60
            else:
                seconds = val
                
            # Extract and clean reminder message
            msg = text
            msg = re.sub(r"\b(in|after|for)\s+\d+\s*(minute|min|second|sec|hour|hr)s?\b", "", msg)
            msg = msg.replace("set a reminder", "").replace("set reminder", "")
            msg = msg.replace("set an alarm", "").replace("set alarm", "")
            msg = msg.replace("set a timer", "").replace("set timer", "")
            msg = msg.replace("remind me to", "").replace("remind me", "")
            msg = msg.strip()
            
            # Remove leading "to " if present
            if msg.startswith("to "):
                msg = msg[3:].strip()
                
            if not msg:
                msg = "Timer finished"
                
            return {"intent": "reminder", "action": "set", "message": msg, "seconds": seconds}
            
        # Fallback to old format if no regex match
        if "remind me to " in text:
            cleaned = text.replace("remind me to ", "").strip()
            parts = cleaned.split(" in ")
            if len(parts) == 2:
                message = parts[0].strip()
                time_info = parts[1].strip()
                seconds = 0
                if "minute" in time_info:
                    seconds = int(time_info.replace("minute", "").replace("s", "").strip()) * 60
                elif "hour" in time_info:
                    seconds = int(time_info.replace("hour", "").replace("s", "").strip()) * 3600
                elif "second" in time_info:
                    seconds = int(time_info.replace("second", "").replace("s", "").strip())
                return {"intent": "reminder", "action": "set", "message": message, "seconds": seconds}
    # ========================
    # news
    # ========================
    if text.startswith("news") or "news" in text:
        return {"intent": "news", "action": "get_headlines"}
    # =========================
    # AGENTIC TASK
    # =========================
    heavy_keywords = ["research ", "analyze ", "write a report", "write a script", "write code", "deep dive", "summarize ", "write an essay", "create a plan", "agent ", "run task "]
    if any(text.startswith(kw) or kw in text for kw in heavy_keywords):
        return {"intent": "agentic", "action": "task", "message": command}

    return None