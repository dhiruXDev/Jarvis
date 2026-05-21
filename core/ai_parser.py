import ollama
import json


SYSTEM_PROMPT = """
You are an AI intent parser for a Jarvis assistant.

Convert user commands into STRICT JSON.

ONLY return JSON.

Examples:

User: open vscode
Output:
{
  "intent": "app",
  "action": "open",
  "target": "vscode"
}

User: write hello in notepad
Output:
{
  "intent": "note",
  "action": "write",
  "content": "hello"
}

User: search python tutorials
Output:
{
  "intent": "web",
  "action": "search",
  "query": "python tutorials"
}
"""


def ai_parse(command):

    try:

        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": command
                }
            ]
        )

        content = response["message"]["content"]

        print("[AI RAW RESPONSE]")
        print(content)

        parsed = json.loads(content)

        return parsed

    except Exception as e:

        print("[AI PARSER ERROR]", e)

        return None