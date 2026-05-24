import time

def analyze(page):
    try:
        # Wait a bit for the submission to process
        time.sleep(10)
        
        # Look for the result text
        result_element = page.locator('.text-green-s, .text-red-s, [data-e2e-locator="submission-result"]')
        if result_element.count() > 0:
            result_text = result_element.first.inner_text()
            speak(f"Result analyzed: {result_text}")
            if "Accepted" in result_text:
                return "The solution was accepted! Great job!"
            else:
                return f"The solution failed with result: {result_text}"
        
        return "Could not determine the result of the submission. You may need to check it manually."
    except Exception as e:
        speak(f"Analyze Error: {e}")
        return "An error occurred while analyzing the result."