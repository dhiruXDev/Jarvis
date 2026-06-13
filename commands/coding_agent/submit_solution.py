import time 

def submit(page):

    try:

        # Click RUN (test case execution)
        page.click(
            'button:has-text("Run")'
        )

        time.sleep(8)

        # Click SUBMIT
        page.click(
            'button:has-text("Submit")'
        )

        print("Solution submitted")
        return True

    except Exception as e:

        print(f"Submit Error: {e}")
        return False