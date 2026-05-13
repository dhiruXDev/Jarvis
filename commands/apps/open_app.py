import subprocess
import webbrowser

WEB_FALLBACKS = {
    "youtube": "https://youtube.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chat.openai.com",
    "leetcode": "https://leetcode.com",
    "spotify": "https://spotify.com"
}

def open_application(app_name):

    app_name = app_name.lower().strip()

    try:

        print(f"[OPEN APP] Trying app: {app_name}")

        # Try opening as application
        subprocess.Popen(app_name)

        return f"Opening {app_name}"

    except Exception as e:

        print(f"[APP ERROR] {e}")

        # =========================
        # WEBSITE FALLBACK
        # =========================
        if app_name in WEB_FALLBACKS:

            url = WEB_FALLBACKS[app_name]

            print(f"[FALLBACK WEBSITE] {url}")

            webbrowser.open(url)

            return f"Opening {app_name} website"

        return f"Unable to open {app_name}"