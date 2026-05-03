import os

def open_app(name):
    if "chrome" in name:
        os.system("start chrome")
    elif "notepad" in name:
        os.system("notepad")