import subprocess
# -------------------------
# Mobile Hotspot Commands
# -------------------------
def run_command(command):

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return result.stdout.strip()

    return result.stderr.strip() or "Command failed"
    
def turn_on_hotspot():
    try:
        # This command may vary depending on the Windows version
        result1 = subprocess.run("netsh wlan set hostednetwork mode=allow ssid=MyHotspot key=12345678", shell=True, capture_output=True, text=True)
        result2 = subprocess.run("netsh wlan start hostednetwork", shell=True, capture_output=True, text=True)
        if result2.returncode == 0:
            return "Mobile hotspot turned on"
        return result2.stderr.strip() or result2.stdout.strip() or "Failed to turn on hotspot"
    except Exception as e:
        return f"Error: {e}"

def turn_off_hotspot():
    try:
        result = subprocess.run("netsh wlan stop hostednetwork", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return "Mobile hotspot turned off"
        return result.stderr.strip() or result.stdout.strip() or "Failed to turn off hotspot"
    except Exception as e:
        return f"Error: {e}"

def show_hotspot_password():
    try:
        result = subprocess.run("netsh wlan show hostednetwork security", shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def open_hotspot_settings():
    try:
        subprocess.run("start ms-settings:network-mobilehotspot", shell=True)
        return "Mobile hotspot settings opened"
    except Exception as e:
        return f"Error: {e}"

def check_hotspot_status():
    try:
        result = subprocess.run("netsh wlan show hostednetwork", shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def disconnect_hotspot():
    try:
        subprocess.run("netsh wlan stop hostednetwork", shell=True)
        return "Mobile hotspot disconnected"
    except Exception as e:
        return f"Error: {e}"

def connect_hotspot(ssid, password):
    try:
        subprocess.run(f'netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}', shell=True)
        subprocess.run("netsh wlan start hostednetwork", shell=True)
        return "Mobile hotspot connected"
    except Exception as e:
        return f"Error: {e}"