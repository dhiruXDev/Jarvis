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
    Convert this command into STRICT JSON.

    Possible intents:
    - open_app
    - open_website
    - search_web
    - exit
    AVAILABLE INTENTS:

    1. open_app
    Use ONLY for desktop applications installed on the PC.

    Examples:
    - open chrome
    - open vscode
    - open spotify app

    2. open_website
    Use for websites/platforms.

    Examples:
    - youtube
    - open github
    - gmail
    - leetcode
    - chatgpt
    - facebook

    3. search_web
    Use when user wants to search something.

    Examples:
    - search python tutorials
    - search ai news
    Examples:

    open chrome
    {{
      "intent": "open_app",
      "target": "chrome"
    }}

    search youtube ai agents
    {{
      "intent": "search_web",
      "query": "youtube ai agents"
    }}

    exit
    {{
      "intent": "exit"
    }}

    Command:
    {cleaned}

    Return ONLY JSON.
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