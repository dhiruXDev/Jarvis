# pyrefly: ignore [missing-import]
import ollama 

def solve_problem(prompt):
    prompt = f"""
        Solve this LeetCode problem.

        Rules:
        - Return ONLY Python code
        - No explanations
        - Use optimal solution
        - Must be directly submittable

        Problem:
        {prompt}
    """
    response = ollama.chat(
        model='qwen2.5:latest',
        messages=[
            {
                'role': 'system',
                'content': "You are a helpful assistant.",
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    )
    speak("Solution generated")
    
    content = response['message']['content']
    import re
    # Remove think tags if present
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    # Try to extract from python code block
    match = re.search(r'```python\n(.*?)\n```', content, flags=re.DOTALL)
    if match:
        code = match.group(1).strip()
    else:
        # Fallback to general code block or raw content
        match = re.search(r'```\n(.*?)\n```', content, flags=re.DOTALL)
        if match:
            code = match.group(1).strip()
        else:
            code = content.strip()
            
    return code