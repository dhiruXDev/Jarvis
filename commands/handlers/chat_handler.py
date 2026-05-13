# pyrefly: ignore [missing-import]
import ollama
# def handle_chat(text):
SYSTEM_PROMPT = """
You are Jarvis, an intelligent AI assistant.

Rules:
- Give accurate factual answers
- Understand cultural references and nicknames
- "God of cricket" commonly refers to Sachin Tendulkar
- Never relate unrelated mythology unless user asks
- Keep answers short and accurate
- If unsure, say you are unsure
"""

def handle_chat(text):
    try:

        response = ollama.chat(

            model='qwen2.5:3b',

            messages=[

                {
                    'role': 'system',

                    'content': """
You are Jarvis.

Rules:
- Give short accurate answers
- Understand common phrases and nicknames
- "God of cricket" usually refers to Sachin Tendulkar
- Avoid unnecessary long explanations
- Reply naturally
"""
                },

                {
                    'role': 'user',
                    'content': text,
                },
            ],

            options={
                "num_predict": 80
            }

        )

        return response['message']['content']

    except Exception as e:

        print("Chat Error:", e)

        return "Sorry, I cannot chat right now."
