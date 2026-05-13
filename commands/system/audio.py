from ctypes import POINTER
from ctypes import cast
# pyrefly: ignore [missing-import]
from comtypes import CLSCTX_ALL
# pyrefly: ignore [missing-import]
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time
import pythoncom

def check_volume():
    try:
        pythoncom.CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume_obj = cast(
            interface,
            POINTER(IAudioEndpointVolume)
        )
        current = int(
            volume_obj.GetMasterVolumeLevelScalar() * 100
        )
        return current
    except Exception as e:
        print(f"Volume Error: {e}")
        return None
        
def volume(level):
    try:
        pythoncom.CoInitialize()
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

def increase_volume(step=10):

    try:

        pythoncom.CoInitialize()

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume_obj = cast(
            interface,
            POINTER(IAudioEndpointVolume)
        )

        current = int(
            volume_obj.GetMasterVolumeLevelScalar() * 100
        )

        new_volume = min(current + step, 100)

        volume_obj.SetMasterVolumeLevelScalar(
            new_volume / 100,
            None
        )

        return True

    except Exception as e:

        print(f"Volume Error: {e}")

        return False

def decrease_volume(step=10):

    try:

        pythoncom.CoInitialize()

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume_obj = cast(
            interface,
            POINTER(IAudioEndpointVolume)
        )

        current = int(
            volume_obj.GetMasterVolumeLevelScalar() * 100
        )

        new_volume = max(current - step, 0)

        volume_obj.SetMasterVolumeLevelScalar(
            new_volume / 100,
            None
        )

        return True

    except Exception as e:

        print(f"Volume Error: {e}")

        return False

def mute_volume():
    try:
        pythoncom.CoInitialize()
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
        pythoncom.CoInitialize()
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
        pythoncom.CoInitialize()
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
