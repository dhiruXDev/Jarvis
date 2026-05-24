import time

def extract_problem(page):

    try:

        page.wait_for_selector('[data-cy="question-title"]')

        title = page.locator(
            '[data-cy="question-title"]'
        ).inner_text()

        description = page.locator(
            '[data-track-load="description_content"]'
        ).inner_text()

        speak("Problem extracted")

        return {
            "title": title,
            "description": description
        }

    except Exception as e:

        speak(f"Extraction Error: {e}")

        return None