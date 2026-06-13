import ollama
from core.speaker import speak

def handle_agentic_task(message):
    try:
        print(f"\n[Agentic Worker] Starting task: {message}\n")
        response = ollama.chat(
            model='qwen2.5:3b',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are Jarvis, an autonomous background AI agent. The user has delegated a heavy or complex task to you. Execute it thoroughly and return the final results. Provide detailed answers if necessary.',
                },
                {
                    'role': 'user',
                    'content': message,
                },
            ]
        )
        result = response['message']['content']
        print(f"\n====================================\n[Agentic Worker Result]\n{result}\n====================================\n")
        
        # Notify the user that the task is complete
        speak("Sir, the background task you requested has been completed. The results are on your screen.")
        
    except Exception as e:
        print("Agentic Worker Error:", e)
        speak("Sir, I encountered an error while processing the background task.")
