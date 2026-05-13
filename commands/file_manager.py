import os
def find_file(filename):
    try:
        # Check current directory
        current_dir = os.getcwd()
        for root, dirs, files in os.walk(current_dir):
            if filename in files:
                return os.path.join(root, filename)

        # If not found, check Desktop
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        for root, dirs, files in os.walk(desktop):
            if filename in files:
                return os.path.join(root, filename)

        return None
    except Exception as e:
        print(f"File search error: {e}")
        return None

def open_file(filename):
    try:
        # Find the file
        file_path = find_file(filename)

        if file_path:
            os.startfile(file_path)
            return f"Opened {filename}"
        else:
            return f"File '{filename}' not found"
    except Exception as e:
        print(f"Open file error: {e}")
        return "Unable to open file"

def delete_file(filename):
    try:
        # Find the file
        file_path = find_file(filename)

        if file_path:
            os.remove(file_path)
            return f"Deleted {filename}"
        else:
            return f"File '{filename}' not found"
    except Exception as e:
        print(f"Delete file error: {e}")
        return "Unable to delete file"