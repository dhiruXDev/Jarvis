import subprocess
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

# show bluetooth devices
def show_bluetooth_devices():
    try:
        return run_command('powershell "Get-PnpDevice -Class Bluetooth"')
    except Exception as e:
        return f"Error: {e}"

# open bluetooth settings 
def open_bluetooth_settings():
    try:
        return run_command('start ms-settings:bluetooth')
    except Exception as e:
        return f"Error: {e}"

# connect bluetooth device
def connect_bluetooth_device(device_name):
    # NOTE: Windows doesn't natively support connecting bluetooth via pure CMD without 3rd party tools.
    return f"Connecting specific Bluetooth devices via CLI is not supported natively. Please use 'open bluetooth settings'."

def turn_on_bluetooth():
    try:
        subprocess.run("reg add HKLM\\SYSTEM\\CurrentControlSet\\Services\\bthserv /v Start /t REG_DWORD /d 2 /f", shell=True)
        return "Bluetooth turned on"
    except Exception as e:
        return f"Error: {e}"

def turn_off_bluetooth():
    try:
        result = subprocess.run(
            r'reg add HKLM\SYSTEM\CurrentControlSet\Services\bthserv /v Start /t REG_DWORD /d 4 /f',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return "Bluetooth turned off"
        return result.stderr.strip() or "Failed to turn off Bluetooth"
    except Exception as e:
        return f"Error: {e}"

def get_connected_devices():
    try:
        result = subprocess.run(
            r'''powershell "Get-PnpDevice -Class Bluetooth |
            Where-Object {
                $_.Status -eq 'OK' -and
                $_.FriendlyName -notmatch 'Enumerator|RFCOMM|Service|Protocol'
            } |
            Select-Object FriendlyName, Status"''',
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    except Exception as e:
        return f"Error: {e}"

def disconnect_bluetooth_device(device_name):
    # NOTE: Windows doesn't natively support disconnecting bluetooth via pure CMD without 3rd party tools.
    return f"Disconnecting specific Bluetooth devices via CLI is not supported natively. Please use 'open bluetooth settings'."