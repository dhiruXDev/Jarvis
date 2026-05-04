import os

def shutdown_pc():
    os.system("shutdown /s /t 1")

def restart_pc():
    os.system("shutdown /r /t 1")

def sleep_pc():
    os.system("shutdown /h")

def volume(level):
    os.system(f"nircmd.exe setvolume 1 {level}%")

def brightness(level):
    os.system(f"nircmd.exe setbrightness {level}%")