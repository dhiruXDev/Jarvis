# pyrefly: ignore [missing-import]
import pygetwindow as gw

# pyrefly: ignore [missing-import]
from fuzzywuzzy import fuzz
    
def minimize_window(app_name):

    try:

        app_name = app_name.lower().strip()

        windows = gw.getAllTitles()

        best_match = None
        best_score = 0

        for title in windows:

            if not title.strip():
                continue

            score = fuzz.partial_ratio(
                app_name,
                title.lower()
            )

            if score > best_score:
                best_score = score
                best_match = title

        if best_match and best_score > 60:

            window = gw.getWindowsWithTitle(best_match)[0]

            window.minimize()

            return f"Minimized {best_match}"

        return f"No window found for {app_name}"

    except Exception as e:

        print(f"Minimize Error: {e}")

        return "Unable to minimize window"



def maximize_window(app_name):

    try:

        app_name = app_name.lower().strip()

        windows = gw.getAllTitles()

        best_match = None
        best_score = 0

        for title in windows:

            if not title.strip():
                continue

            score = fuzz.partial_ratio(
                app_name,
                title.lower()
            )

            if score > best_score:
                best_score = score
                best_match = title

        if best_match and best_score > 60:

            window = gw.getWindowsWithTitle(best_match)[0]

            window.maximize()

            return f"Maximized {best_match}"

        return f"No window found for {app_name}"

    except Exception as e:

        print(f"Maximize Error: {e}")

        return "Unable to maximize window"

def close_window(app_name):

    try:

        app_name = app_name.lower().strip()

        windows = gw.getAllTitles()

        for title in windows:

            if app_name in title.lower():

                window = gw.getWindowsWithTitle(title)[0]

                window.close()

                return f"Closed {title}"

        return f"No window found for {app_name}"

    except Exception as e:

        print(f"Close Error: {e}")

        return "Unable to close window"
