# import subprocess
# import webbrowser

# WEB_FALLBACKS = {
#     "youtube": "https://youtube.com",
#     "github": "https://github.com",
#     "gmail": "https://mail.google.com",
#     "chatgpt": "https://chat.openai.com",
#     "leetcode": "https://leetcode.com",
#     "spotify": "https://spotify.com"
# }
# # WINDOWS APP MAPPINGS
# APP_MAPPINGS = {
#     "calculator": "calc.exe",
#     "calc": "calc.exe",
#     "notepad": "notepad.exe",
#     "paint": "mspaint.exe",
#     "cmd": "cmd.exe",
#     "command prompt": "cmd.exe",
#     "windows explorer": "explorer.exe",
#     "wexplorer": "explorer.exe",
#     "clock": "ms-clock:"
# }
# def open_application(app_name):

#     app_name = app_name.lower().strip()

#     try:

#         print(f"[OPEN APP] Trying app: {app_name}")

#         # Try opening as application
#         executable = APP_MAPPINGS.get(app_name, app_name)
#         subprocess.Popen(executable, shell=True)

#         return f"Opening {app_name}"

#     except Exception as e:

#         print(f"[APP ERROR] {e}")

#         # =========================
#         # WEBSITE FALLBACK
#         # =========================
#         if app_name in WEB_FALLBACKS:
#             url = WEB_FALLBACKS[app_name]
#             print(f"[FALLBACK WEBSITE] {url}")
#             webbrowser.open(url)
#             return f"Opening {app_name} website"
#         return f"Unable to open {app_name}"

import subprocess
import webbrowser
import os

WEB_FALLBACKS = {
    "youtube": "https://youtube.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chat.openai.com",
}

APP_MAPPINGS = {
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "notepad": "notepad.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
}

WINDOWS_URI = {
    "clock": "ms-clock:",
    "alarm": "ms-clock:",
    "camera": "microsoft.windows.camera:",
    "settings": "ms-settings:",
    "store": "ms-windows-store:",
}

def open_application(app_name):

    app_name = app_name.lower().strip()

    print(f"[OPEN APP] Trying: {app_name}")

    # =========================
    # 1. NORMAL EXE APPS
    # =========================
    if app_name in APP_MAPPINGS:
        try:
            subprocess.run(APP_MAPPINGS[app_name], shell=True, check=True)
            return f"Opening {app_name}"
        except Exception as e:
            print(f"[EXE ERROR] {e}")

    # =========================
    # 2. WINDOWS URI APPS
    # =========================
    if app_name in WINDOWS_URI:
        try:
            os.startfile(WINDOWS_URI[app_name])
            return f"Opening {app_name}"
        except Exception as e:
            print(f"[URI ERROR] {e}")

    # =========================
    # 3. WEBSITE FALLBACK
    # =========================
    if app_name in WEB_FALLBACKS:
        webbrowser.open(WEB_FALLBACKS[app_name])
        return f"Opening {app_name} website"

    return f"Unable to open {app_name}"