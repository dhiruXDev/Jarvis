# # import json
# # import re
# # import requests
# # from core.logger import log_command
# # from core.local_parser import local_parse

# # OLLAMA_URL = "http://localhost:11434/api/generate"
# # MODEL_NAME = "qwen2.5:1.5b"

# # def extract_json(text):

# #     try:
# #         return json.loads(text)

# #     except json.JSONDecodeError:

# #         match = re.search(r"\{.*?\}", text, re.DOTALL)

# #         if match:
# #             try:
# #                 return json.loads(match.group())
# #             except:
# #                 pass

# #     return {"intent": "chat", "message": text}

# # def ask_ollama(prompt):

# #     response = requests.post(
# #         OLLAMA_URL,
# #         json={
# #             "model": MODEL_NAME,
# #             "prompt": prompt,
# #             "stream": False
# #         },
# #         timeout=30
# #     )

# #     response.raise_for_status()

# #     result = response.json()

# #     return result.get("response", "").strip()

# # def process(command):
# #     cleaned = command.lower().strip()
# #     print("Cleaned Text:", cleaned)
# #     log_command(cleaned)

# #     # FIRST TRY LOCAL PARSER
# #     local_result = local_parse(cleaned)

# #     if local_result:
# #         print("Done by local parser:", local_result)
# #         return local_result


# #     prompt = f"""

# # You are Jarvis, a smart AI assistant.

# # Rules:
# # - Give accurate factual answers
# # - Do not hallucinate
# # - If unsure, say you are unsure
# # - Understand common nicknames and phrases
# # - Reply naturally and briefly
# # - Avoid making up facts
# # Convert the user command into JSON.

# # ONLY return valid JSON.
# # INTENTS:

# # 1. search_web
# # Use ONLY when the user explicitly wants
# # to search on Google, browser, YouTube, or internet.

# # Examples:
# # - search python tutorials
# # - google linked list
# # - search ai news
# # - find laptop reviews online

# # Output:
# # {{"intent":"search_web","query":"user query"}}


# # 2. chat
# # Use when the user wants explanation,
# # conversation, learning, coding help,
# # or general discussion.

# # Examples:
# # - explain linked list
# # - what is python
# # - tell me a joke

# # Output:
# # {{"intent":"chat","message":"user message"}}


# # 3. open_app

# # Example:
# # open chrome

# # Output:
# # {{"intent":"open_app","target":"chrome"}}


# # 4. open_website

# # Example:
# # open youtube

# # Output:
# # {{"intent":"open_website","target":"youtube"}}


# # 5. volume_control

# # Example:
# # volume 50

# # Output:
# # {{"intent":"volume_control","level":50}}


# # 6. send_whatsapp_message

# # Example:
# # send hello to aman

# # Output:
# # {{"intent":"send_whatsapp_message","contact":"aman","message":"hello"}}


# # 7. close_app

# # Example:
# # close chrome

# # Output:
# # {{"intent":"close_app","target":"chrome"}}


# # 8. exit

# # Example:
# # exit

# # Output:
# # {{"intent":"exit"}}


# # USER COMMAND:
# # {cleaned}
# # """

# #     try:

# #         text = ask_ollama(prompt)

# #         print("AI RAW:", text)

# #         data = extract_json(text)

# #         print("AI PARSED:", data)

# #         return data

# #     except requests.exceptions.Timeout:

# #         print("AI Error: Request timed out")
# #         return {"intent": "unknown"}

# #     except requests.exceptions.ConnectionError:

# #         print("AI Error: Ollama not running")
# #         return {"intent": "unknown"}

# #     except Exception as e:

# #         print("AI Error:", e)

# #         return {"intent": "unknown"}


# import json
# import re
# import requests

# from core.logger import log_command
# from core.local_parser import local_parse


# OLLAMA_URL = "http://localhost:11434/api/generate"

# # Better model recommended:
# # qwen2.5:7b
# # llama3.1:8b
# MODEL_NAME = "qwen2.5:3b"


# def extract_json(text):

#     """
#     Extract valid JSON from Ollama response
#     """

#     try:
#         return json.loads(text)

#     except json.JSONDecodeError:

#         # remove markdown code blocks
#         text = text.replace("```json", "")
#         text = text.replace("```", "")

#         match = re.search(
#             r"\{.*?\}",
#             text,
#             re.DOTALL
#         )

#         if match:

#             try:
#                 return json.loads(match.group())

#             except:
#                 pass

#     return {
#         "intent": "chat",
#         "message": text
#     }


# def ask_ollama(prompt):

#     """
#     Sends prompt to Ollama
#     """

#     response = requests.post(
#         OLLAMA_URL,
#         json={
#             "model": MODEL_NAME,
#             "prompt": prompt,
#             "stream": True, 
#             "num_predict":100
#         },
#         timeout=30
#     )

#     response.raise_for_status()

#     result = response.json()

#     return result.get("response", "").strip()


# def process(command):

#     """
#     Main Brain Function
#     """

#     cleaned = command.lower().strip()

#     print("Cleaned Text:", cleaned)

#     log_command(cleaned)

#     # ====================================================
#     # STEP 1 — LOCAL PARSER
#     # ====================================================

#     local_result = local_parse(cleaned)

#     if local_result:

#         print("[LOCAL PARSER USED]")

#         print(local_result)

#         return local_result

#     # ====================================================
#     # STEP 2 — AI FALLBACK
#     # ====================================================

#     print("[FALLING BACK TO OLLAMA]")

#     prompt = f"""
# You are Jarvis Intent Classifier.

# Your job:
# Convert user commands into STRICT JSON.

# IMPORTANT RULES:
# - Return ONLY valid JSON
# - Do NOT use markdown
# - Do NOT explain anything
# - Do NOT write ```json
# - Never invent fields
# - Never invent intents

# ====================================================
# AVAILABLE INTENTS
# ====================================================

# 1. search_web

# Use ONLY when user explicitly wants
# internet or browser search.

# Examples:
# - search python tutorials
# - google linked list
# - search ai news
# - find laptop reviews online

# Output:
# {{"intent":"search_web","query":"user query"}}


# ====================================================

# 2. chat

# Use for:
# - explanations
# - learning
# - coding help
# - factual questions
# - conversation
# - jokes
# - general discussion

# Examples:
# - explain linked list
# - what is python
# - teach me recursion
# - tell me a joke

# Output:
# {{"intent":"chat","message":"user message"}}


# ====================================================

# 3. open_app

# Examples:
# - open chrome
# - launch vscode

# Output:
# {{"intent":"open_app","target":"app_name"}}


# ====================================================

# 4. open_website

# Examples:
# - open youtube
# - open github

# Output:
# {{"intent":"open_website","target":"website_name"}}


# ====================================================

# 5. volume_control

# Examples:
# - volume 50
# - set volume to 80

# Output:
# {{"intent":"volume_control","level":50}}


# ====================================================

# 6. brightness_control

# Examples:
# - brightness 40
# - set brightness to 70

# Output:
# {{"intent":"brightness_control","level":70}}


# ====================================================

# 7. send_whatsapp_message

# Examples:
# - send hello to aman
# - whatsapp rahul good morning

# Output:
# {{"intent":"send_whatsapp_message","contact":"name","message":"message"}}


# ====================================================

# 8. close_app

# Examples:
# - close chrome
# - close spotify

# Output:
# {{"intent":"close_app","target":"app_name"}}


# ====================================================

# 9. play_song

# Examples:
# - play believer
# - play shape of you

# Output:
# {{"intent":"play_song","song_name":"song"}}


# ====================================================

# 10. system_control

# Actions:
# - shutdown
# - restart
# - sleep
# - lock
# - mute
# - unmute
# - time
# - date
# - check_battery

# Examples:
# - shutdown pc
# - mute volume
# - what is time

# Output:
# {{"intent":"system_control","action":"action_name"}}


# ====================================================

# 11. exit

# Examples:
# - exit
# - quit
# - stop jarvis

# Output:
# {{"intent":"exit"}}


# ====================================================

# USER COMMAND:
# {cleaned}
# """

#     try:

#         text = ask_ollama(prompt)

#         print("AI RAW:", text)

#         data = extract_json(text)

#         print("AI PARSED:", data)

#         return data

#     except requests.exceptions.Timeout:

#         print("AI Error: Request timed out")

#         return {
#             "intent": "unknown"
#         }

#     except requests.exceptions.ConnectionError:

#         print("AI Error: Ollama not running")

#         return {
#             "intent": "unknown"
#         }

#     except Exception as e:

#         print("AI Error:", e)

#         return {
#             "intent": "unknown"
#         }


from core.logger import log_command
from core.local_parser import local_parse


def process(command):

    cleaned = command.lower().strip()

    print("Cleaned Text:", cleaned)

    log_command(cleaned)

    # ============================================
    # STEP 1 — LOCAL PARSER
    # ============================================

    local_result = local_parse(cleaned)

    if local_result:

        print("[LOCAL PARSER USED]")

        print(local_result)

        return local_result

    # ============================================
    # STEP 2 — CHAT FALLBACK
    # ============================================

    print("[CHAT FALLBACK]")

    return {
        "intent": "chat",
        "message": cleaned
    }