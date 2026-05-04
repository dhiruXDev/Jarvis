import os
import json
import re
from dotenv import load_dotenv
from google import genai
from utils.cleaner import clean_command
from core.router import route_command
from core.logger import log_command

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return {"intent": "unknown"}
    return {"intent": "unknown"}


# def process(command):
#     prompt = f"""
#     Convert this command into STRICT JSON.

#     Command: {command}

#     Examples:
#     open chrome → {{"intent": "open_app", "target": "chrome"}}
#     open youtube → {{"intent": "search", "query": "youtube"}}
#     type hello → {{"intent": "type", "text": "hello"}}

#     Only return JSON.
#     """

#     try:
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",   # ✅ FIXED MODEL
#             contents=prompt
#         )

#         text = response.text.strip()
#         print("AI RAW:", text)

#         return extract_json(text)

#     except Exception as e:
#         print("AI Error:", e)
#         return {"intent": "unknown"}

def process(command):

    cleaned = clean_command(command)

    log_command(cleaned)

    prompt = f"""
    You are an AI intent parser for a desktop assistant called Jarvis.

    Your job is to convert user commands into STRICT JSON.

    ━━━━━━━━━━━━━━━━━━━━
    ALLOWED INTENTS
    ━━━━━━━━━━━━━━━━━━━━

    1. open_app
    Use ONLY for desktop applications installed on the computer.

    Schema:
    {{
      "intent": "open_app",
      "target": "app_name"
    }}

    Examples:
    open chrome
    open vscode
    launch spotify
    chrome kholna


    ━━━━━━━━━━━━━━━━━━━━

    2. open_website
    Use for websites, online platforms, and browser services.

    Schema:
    {{
      "intent": "open_website",
      "target": "website_name"
    }}

    Examples:
    youtube
    open github
    gmail
    leetcode
    chatgpt
    facebook
    github kholo


    ━━━━━━━━━━━━━━━━━━━━

    3. search_web
    Use when the user wants to search something online.

    Schema:
    {{
      "intent": "search_web",
      "query": "search query"
    }}

    Examples:
    search python tutorials
    search ai news
    search youtube transformers
    google machine learning roadmap


    ━━━━━━━━━━━━━━━━━━━━

    4. open_potd
    Use when the user wants LeetCode Problem of the Day.

    Schema:
    {{
      "intent": "open_potd"
    }}

    Examples:
    open problem of the day
    leetcode potd
    potd kholo
    daily coding problem


    ━━━━━━━━━━━━━━━━━━━━

    5. system_control
    Use for system-level commands.

    Schema:
    {{
      "intent": "system_control",
      "action": "action_name"
    }}

    AVAILABLE ACTIONS:
    - shutdown
    - restart
    - sleep
    - lock
    - check_battery

    Examples:
    shutdown pc
    restart computer
    lock system
    sleep pc
    battery check


    ━━━━━━━━━━━━━━━━━━━━

    6. volume_control
    Use for volume changes.

    Schema:
    {{
      "intent": "volume_control",
      "level": number
    }}

    Examples:
    set volume to 50
    volume 80 percent
    increase volume to 70


    ━━━━━━━━━━━━━━━━━━━━

    7. brightness_control
    Use for brightness changes.

    Schema:
    {{
      "intent": "brightness_control",
      "level": number
    }}

    Examples:
    set brightness to 40
    brightness 70 percent


    ━━━━━━━━━━━━━━━━━━━━

    8. exit

    Schema:
    {{
      "intent": "exit"
    }}

    Examples:
    exit
    quit
    goodbye
    stop jarvis


    ━━━━━━━━━━━━━━━━━━━━
    IMPORTANT RULES
    ━━━━━━━━━━━━━━━━━━━━

    - Return ONLY valid JSON.
    - Do NOT use markdown.
    - Do NOT use ```json.
    - Never explain anything.
    - Never invent new intents.
    - Never invent new fields.
    - Use ONLY the intents listed above.
    - Commands may be multilingual.
    - "gmail", "youtube", "github", "leetcode", and "chatgpt" are websites, NOT apps.

    ━━━━━━━━━━━━━━━━━━━━

    USER COMMAND:
    {cleaned}
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        print("AI RAW:", text)

        data = extract_json(text)

        return data

    except Exception as e:

        print("AI Error:", e)

        return {"intent": "unknown"}