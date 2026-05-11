import json
import re
import requests
from core.logger import log_command
from core.local_parser import local_parse

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

def extract_json(text):

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        match = re.search(r"\{.*?\}", text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return {"intent": "chat", "message": text}


def ask_ollama(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return result.get("response", "").strip()


def process(command):
    cleaned = command.lower().strip()
    print("Cleaned Text:", cleaned)
    log_command(cleaned)

    # FIRST TRY LOCAL PARSER
    local_result = local_parse(cleaned)

    if local_result:
        print("Done by local parser:", local_result)
        return local_result


    prompt = f"""
Convert the user command into JSON.
ONLY return valid JSON.

Examples:
Search_web - Use ONLY when the user explicitly wants
to search on Google, browser, YouTube, or internet.

Examples:
- search python tutorials
- google linked list
- search ai news
- find laptop reviews online

Output:
{{"intent":"search_web","query":"user query"}}


chat - Use when the user wants explanation,
conversation, learning, coding help,
or general discussion.

Examples:
- explain linked list
- what is python
- teach me recursion
- who is elon musk
- tell me a joke

Output:
{{"intent":"chat","message":"user message"}}
open chrome
{{"intent":"open_app","target":"chrome"}}

open youtube
{{"intent":"open_website","target":"youtube"}}

volume 50
{{"intent":"volume_control","level":50}}

search python tutorials
{{"intent":"search_web","query":"python tutorials"}}

send hello to aman
{{"intent":"send_whatsapp_message","contact":"aman","message":"hello"}}

search python tutorials
{"intent":"search_web","query":"python tutorials"}

close chrome
{{"intent":"close_app","target":"chrome"}}

exit
{{"intent":"exit"}}

If command is normal conversation, Send funny answers:
{{"intent":"chat","message":"user_message"}}

USER COMMAND:
{cleaned}
"""

    try:

        text = ask_ollama(prompt)

        print("AI RAW:", text)

        data = extract_json(text)

        print("AI PARSED:", data)

        return data

    except requests.exceptions.Timeout:

        print("AI Error: Request timed out")
        return {"intent": "unknown"}

    except requests.exceptions.ConnectionError:

        print("AI Error: Ollama not running")
        return {"intent": "unknown"}

    except Exception as e:

        print("AI Error:", e)

        return {"intent": "unknown"}