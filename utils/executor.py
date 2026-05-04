 
# from core.speaker import speak
# import actions.system as system
# import actions.typing as typing
# import webbrowser

# def execute(intent):
#     if intent["intent"] == "open_app":
#         speak(f"Opening {intent['target']}")
#         system.open_app(intent["target"])

#     elif intent["intent"] == "type":
#         speak("Typing now")
#         typing.type_text(intent["text"])

#     elif intent["intent"] == "exit":
#         speak("Shutting down")
#         return False

#     elif intent["intent"] == "search":
#         speak("Searching now")
#         webbrowser.open(f"https://www.google.com/search?q={intent['query']}")
    
#     else:
#         speak("I did not understand")

#     return True

# import actions.system as system
# import actions.typing as typing
# import webbrowser
# from modules.multilang import translator

# def execute(intent, lang="en"):
#     if intent["intent"] == "open_app":
#         msg = f"Opening {intent['target']} now"
#         translated = translator.from_english(msg, lang)
#         translator.speak(translated, lang)

#         system.open_app(intent["target"])
#         return msg

#     elif intent["intent"] == "type":
#         msg = "I am typing now"
#         translated = translator.from_english(msg, lang)
#         translator.speak(translated, lang)

#         typing.type_text(intent["text"])
#         return msg

#     elif intent["intent"] == "search":
#         msg = f"I am searching {intent['query']}"
#         translated = translator.from_english(msg, lang)
#         translator.speak(translated, lang)


#         webbrowser.open(f"https://www.google.com/search?q={intent['query']}")
#         return msg

#     elif intent["intent"] == "exit":
#         msg = "Shutting down"
#         translated = translator.from_english(msg, lang)
#         translator.speak(translated, lang)
#         return msg

#     else:
#         msg = "I did not understand"
#         translated = translator.from_english(msg, lang)
#         translator.speak(translated, lang)
#         return msg


from commands.open_app import open_application
from commands.search_web import search_google
from commands.open_website import open_website
from commands.coding import open_potd_leetcode, open_potd_gfg
from commands.system import shutdown_pc, restart_pc, sleep_pc, lock, volume, check_battery, brightness

def execute(intent, lang=None):
    print(intent)
    if intent["intent"] == "open_app":
        target = intent["target"]
        open_application(target)
        return f"Opening {target}"

    elif intent["intent"] == "search_web":
        query = intent["query"]
        search_google(query)
        return f"Searching {query}"

    elif intent["intent"] == "open_website":
        target = intent["target"]
        open_website(target)
        return f"Opening {target}"

    elif intent["intent"] == "open_potd_leetcode":
        return open_potd_leetcode()
    
    elif intent["intent"] == "open_potd_gfg":
        return open_potd_gfg()

    elif intent["intent"] == "system_control":
        print("SYSTEM CONTROL DETECTED")
        action = intent["action"]
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
            print("CHECKING BATTERY")
            return check_battery

        elif intent["intent"] == "brightness_control":
            level = intent["level"]
            brightness(level)
            return f"Setting brightness to {level}"
        
        elif intent["intent"] == "volume_control":
            level = intent["level"]
            volume(level)
            return f"Setting volume to {level} "

    else:
        return "I did not understand the command"