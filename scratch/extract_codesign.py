import os
import subprocess
import shutil

cache_dir = r"C:\Users\HP\AppData\Local\electron-builder\Cache\winCodeSign"
archive_path = os.path.join(cache_dir, "101117055.7z") # Use any downloaded archive
output_dir = os.path.join(cache_dir, "winCodeSign-2.6.0")
zip_bin = r"E:\Project\Jarvish\node_modules\7zip-bin\win\x64\7za.exe"

if not os.path.exists(archive_path):
    # fallback to first found .7z file
    files = [f for f in os.listdir(cache_dir) if f.endswith(".7z")]
    if files:
        archive_path = os.path.join(cache_dir, files[0])
    else:
        raise FileNotFoundError("No .7z archive found in winCodeSign cache directory.")

print(f"Extracting from: {archive_path}")
print(f"Target directory: {output_dir}")

# Remove existing target dir if any
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

# Run 7za with exclude flags for darwin and linux folders (which contain the offending symlinks)
cmd = [
    zip_bin,
    "x",
    "-bd",
    archive_path,
    f"-o{output_dir}",
    "-x!darwin",
    "-x!linux"
]

print("Running command:", " ".join(cmd))
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

print("Exit code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)

if res.returncode == 0:
    print("[SUCCESS] winCodeSign extracted successfully without non-Windows symlinks.")
    # Clean up temporary folders created by failed attempts
    for item in os.listdir(cache_dir):
        full_path = os.path.join(cache_dir, item)
        if os.path.isdir(full_path) and item != "winCodeSign-2.6.0":
            print(f"Cleaning up failed extract folder: {item}")
            shutil.rmtree(full_path)
else:
    print("[ERROR] Extraction failed.")
