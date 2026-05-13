import subprocess
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
