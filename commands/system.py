import subprocess
import psutil
import screen_brightness_control as sbc
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


# def volume(level):

#     try:

#         # Keep value between 0 and 100
#         level = max(0, min(int(level), 100))

#         # Convert to Windows scale
#         volume_value = int((level / 100) * 65535)

#         subprocess.run(
#             ["nircmd.exe", "setsysvolume", str(volume_value)],
#             check=True
#         )

#         return True

#     except Exception as e:
#         print(f"Volume Error: {e}")
#         return False

def volume(level):
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

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