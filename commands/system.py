import subprocess
import psutil
import screen_brightness_control as sbc
from datetime import datetime
import time

import pygetwindow as gw
from fuzzywuzzy import fuzz
import os

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

def shutdown_pc():
    try:
        subprocess.run(
            ["shutdown", "/s", "/t", "1"],
            check=True
        )
        return True

    except Exception as e:
        print(f"Shutdown Error: {e}")
        return False


def restart_pc():
    try:
        subprocess.run(
            ["shutdown", "/r", "/t", "1"],
            check=True
        )
        return True

    except Exception as e:
        print(f"Restart Error: {e}")
        return False


def sleep_pc():
    try:
        subprocess.run(
            ["shutdown", "/h"],
            check=True
        )
        return True

    except Exception as e:
        print(f"Sleep Error: {e}")
        return False


def lock():
    try:
        subprocess.run(
            ["rundll32.exe", "user32.dll,LockWorkStation"],
            check=True
        )
        return True

    except Exception as e:
        print(f"Lock Error: {e}")
        return False

def volume(level):
    try:
        

        level = max(0, min(int(level), 100))

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume_obj = cast(interface, POINTER(IAudioEndpointVolume))

        volume_obj.SetMasterVolumeLevelScalar(level / 100.0, None)

        return True

    except Exception as e:
        print(f"Volume Error: {e}")
        return False

def check_battery():

    try:

        battery = psutil.sensors_battery()

        if battery is None:
            return "Battery information not available"

        percent = battery.percent
        plugged = battery.power_plugged

        if plugged:
            return f"Battery is {percent}% and charging"

        return f"Battery is {percent}%"

    except Exception as e:
        print(f"Battery Error: {e}")
        return "Unable to check battery"


def brightness(level):

    try:

        # Keep value between 0 and 100
        level = max(0, min(int(level), 100))

        sbc.set_brightness(level)

        return True

    except Exception as e:
        print(f"Brightness Error: {e}")
        return False

def current_time():

    try:

        now = datetime.now()

        return now.strftime("Time is %I:%M %p")

    except Exception as e:
        print(f"Time Error: {e}")
        return "Unable to get time"


def current_date():

    try:

        today = datetime.now()

        return today.strftime("Today's date is %d %B %Y")

    except Exception as e:
        print(f"Date Error: {e}")
        return "Unable to get date"

def mute_volume():

    try:

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume_obj = cast(interface, POINTER(IAudioEndpointVolume))

        volume_obj.SetMute(1, None)

        return True

    except Exception as e:
        print(f"Mute Error: {e}")
        return False


def unmute_volume():

    try:

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume_obj = cast(interface, POINTER(IAudioEndpointVolume))

        volume_obj.SetMute(0, None)

        return True

    except Exception as e:
        print(f"Unmute Error: {e}")
        return False

def keep_quiet(minutes):

    try:

        minutes = int(minutes)

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume_obj = cast(interface, POINTER(IAudioEndpointVolume))

        # Save current volume
        current_volume = volume_obj.GetMasterVolumeLevelScalar()

        # Mute
        volume_obj.SetMute(1, None)

        print(f"Muted for {minutes} minutes")

        # Wait
        time.sleep(minutes * 60)

        # Unmute
        volume_obj.SetMute(0, None)

        # Restore old volume
        volume_obj.SetMasterVolumeLevelScalar(
            current_volume,
            None
        )

        return True

    except Exception as e:
        print(f"Quiet Mode Error: {e}")
        return False

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


