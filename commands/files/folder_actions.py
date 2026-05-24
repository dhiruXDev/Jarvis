import os
def open_downloads():
    try:
        download_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        os.startfile(download_path)
        return "Downloads folder opened"
    except Exception as e:
        speak(f"Open downloads error: {e}")
        return "Unable to open downloads folder"

def open_desktop():
    try:
        desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        os.startfile(desktop_path)
        return "Desktop folder opened"
    except Exception as e:
        speak(f"Open desktop error: {e}")
        return "Unable to open desktop folder"

def open_documents():
    try:
        documents_path = os.path.join(os.environ['USERPROFILE'], 'Documents')
        os.startfile(documents_path)
        return "Documents folder opened"
    except Exception as e:
        speak(f"Open documents error: {e}")
        return "Unable to open documents folder"

def open_drives():
    try:
        drives_path = os.path.join(os.environ['USERPROFILE'], 'Drives')
        os.startfile(drives_path)
        return "Drives folder opened"
    except Exception as e:
        speak(f"Open drives error: {e}")
        return "Unable to open drives folder"

def open_folder(folder_name):
    try:
        folder_path = os.path.join(os.environ['USERPROFILE'], folder_name)
        os.startfile(folder_path)
        return f"{folder_name} folder opened"
    except Exception as e:
        speak(f"Open {folder_name} error: {e}")
        return f"Unable to open {folder_name} folder"