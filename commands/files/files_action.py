import os
def find_file(filename):
    try:
        filename = filename.lower()
        search_locations = [
            os.getcwd(),
            os.path.join(
                os.environ['USERPROFILE'],
                'Desktop'
            ),
            os.path.join(
                os.environ['USERPROFILE'],
                'Downloads'
            ),
            os.path.join(
                os.environ['USERPROFILE'],
                'Documents'
            )
        ]
        for location in search_locations:
            for root, dirs, files in os.walk(location):
                for file in files:
                    if filename in file.lower():
                        return os.path.join(root, file)
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