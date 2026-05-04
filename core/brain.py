 
# def process(command):
#     command = command.lower()

#     if "notepad" in command:
#         return {"intent": "open_app", "target": "notepad"}

#     elif "chrome" in command:
#         return {"intent": "open_app", "target": "chrome"}

#     elif "type" in command:
#         text = command.replace("type", "").strip()
#         return {"intent": "type", "text": text}

#     elif "exit" in command or "stop" in command:
#         return {"intent": "exit"}

#     return {"intent": "unknown"}

# import google.generativeai as genai
# import os
# import json
# from dotenv import load_dotenv

# load_dotenv()

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# model = genai.GenerativeModel("gemini-pro")

# def process(command):
#     prompt = f"""
#     Convert the following command into STRICT JSON.

#     Command: {command}

#     Examples:
#     open chrome → {{"intent": "open_app", "target": "chrome"}}
#     type hello world → {{"intent": "type", "text": "hello world"}}
#     search python → {{"intent": "search", "query": "python"}}

#     Only return JSON. No explanation.
#     """

#     try:
#         response = model.generate_content(prompt)
#         text = response.text.strip()

#         return json.loads(text)

#     except:
#         return {"intent": "unknown"}
import os
import json
import re
from dotenv import load_dotenv
from google import genai

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


def process(command):
    prompt = f"""
    Convert this command into STRICT JSON.

    Command: {command}

    Examples:
    open chrome → {{"intent": "open_app", "target": "chrome"}}
    open youtube → {{"intent": "search", "query": "youtube"}}
    type hello → {{"intent": "type", "text": "hello"}}

    Only return JSON.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",   # ✅ FIXED MODEL
            contents=prompt
        )

        text = response.text.strip()
        print("AI RAW:", text)

        return extract_json(text)

    except Exception as e:
        print("AI Error:", e)
        return {"intent": "unknown"}