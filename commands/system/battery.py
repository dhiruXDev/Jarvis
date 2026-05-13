import psutil

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
