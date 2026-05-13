import subprocess 
import time

# -------------------------
# Wi-Fi Commands
# -------------------------

def turn_on_wifi():
    try:
        subprocess.run('netsh interface set interface "Wi-Fi" enabled', shell=True)
        return "Wi-Fi turned on"
    except Exception as e:
        return f"Error: {e}"

def turn_off_wifi():
    try:
        subprocess.run('netsh interface set interface "Wi-Fi" disabled', shell=True)
        return "Wi-Fi turned off"
    except Exception as e:
        return f"Error: {e}"

# -------------------------
# Wi-Fi Connection Commands
# -------------------------

def show_wifi_networks():
    try:
        result = subprocess.run("netsh wlan show networks", shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def connect_wifi(ssid):
    try:
        subprocess.run(f"netsh wlan connect name={ssid}", shell=True)
        return f"Connected to {ssid}"
    except Exception as e:
        return f"Error: {e}"

def connect_wifi_password(ssid, password):
    try:
        # Note: netsh wlan connect doesn't directly support password via command line easily without profiles, 
        # but maintaining the signature for executor.py
        subprocess.run(f"netsh wlan connect name={ssid} key={password}", shell=True)
        return f"Connected to {ssid}"
    except Exception as e:
        return f"Error: {e}"

def show_wifi_settings():
    try:
        subprocess.run("start ms-settings:network-wifi", shell=True)
        return "Wi-Fi settings opened"
    except Exception as e:
        return f"Error: {e}"

def disconnect_wifi():
    try:
        subprocess.run(
        "netsh wlan disconnect",
        shell=True
    )
        return "Wi-Fi disconnected"
    except Exception as e:
        return f"Error: {e}"

def check_wifi_status():
    try:
        result = subprocess.run("netsh wlan show hostednetwork", shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def show_wifi_password(ssid=""):
    if not ssid:
        return "Please provide the network name to show its password."
    result = subprocess.run(
        f'netsh wlan show profile name="{ssid}" key=clear',
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout
