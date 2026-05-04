import os
import psutil

def shutdown_pc():
    os.system("shutdown /s /t 1")

def restart_pc():
    os.system("shutdown /r /t 1")

def sleep_pc():
    os.system("shutdown /h")

def lock():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    
def volume(level):
    os.system(f"nircmd.exe setvolume 1 {level}")


def check_battery():
    battery = psutil.sensors_battery()
    if battery is None:
        return "Battery information not available"
    percent = battery.percent
    plugged = battery.power_plugged
    if plugged:
        return f"Battery is {percent} percent and charging"
    return f"Battery is {percent} percent"
    
def brightness(level):
    os.system(f"nircmd.exe setbrightness {level}")