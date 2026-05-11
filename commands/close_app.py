import pygetwindow as gw
import pyautogui
import time


def close_application(app_name):

    try:

        app_name = app_name.lower().strip()

        windows = gw.getAllTitles()

        for title in windows:

            if app_name in title.lower():

                window = gw.getWindowsWithTitle(title)[0]

                # restore if minimized
                if window.isMinimized:
                    window.restore()

                # safer focus trick
                window.minimize()
                window.restore()

                time.sleep(0.5)

                # close selected window only
                pyautogui.hotkey("alt", "f4")
                return f"Closed {title}"

        return f"No open window found for {app_name}"

    except Exception as e:

        print(f"Close App Error: {e}")

        return "Unable to close application"