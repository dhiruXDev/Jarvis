# pyrefly: ignore [missing-import]
import screen_brightness_control as sbc
def brightness(level):
    try:
        level = max(0, min(int(level), 100))
        sbc.set_brightness(level)
        return True

    except Exception as e:
        print(f"Brightness Error: {e}")
        return False

def brightness_up():
    try:
        current_brightness = sbc.get_brightness()
        new_brightness = current_brightness[0] + 10
        sbc.set_brightness(new_brightness)
        return True
    except Exception as e:
        print(f"Brightness Error: {e}")
        return False

def brightness_down():
    try:
        current_brightness = sbc.get_brightness()
        new_brightness = current_brightness[0] - 10
        sbc.set_brightness(new_brightness)
        return True
    except Exception as e:
        print(f"Brightness Error: {e}")
        return False

def get_brightness():
    try:
        brightness = sbc.get_brightness()
        if isinstance(brightness, list):
            brightness = brightness[0]
        return f"Brightness is {brightness}%"

    except Exception as e:
        print(f"Brightness Error: {e}")
        return None
