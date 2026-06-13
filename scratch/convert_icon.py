import os
from PIL import Image

png_path = r"C:\Users\HP\.gemini\antigravity-ide\brain\9db0349e-ae85-49c5-b803-9f6473fa2ce5\jarvis_icon_1781265060202.png"
assets_dir = r"e:\Project\Jarvish\assets"

os.makedirs(assets_dir, exist_ok=True)

# Save as PNG
img = Image.open(png_path)
img.save(os.path.join(assets_dir, "icon.png"))
print("Saved PNG icon.")

# Save as ICO (standard sizes)
img.save(os.path.join(assets_dir, "icon.ico"), sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
print("Saved ICO icon.")
