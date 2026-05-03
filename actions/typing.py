import pyautogui
import time

def type_text(text):
    time.sleep(2)  # time to switch window
    pyautogui.write(text, interval=0.03)