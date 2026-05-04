import webbrowser

SITES = {
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "leetcode": "https://leetcode.com",
    "chatgpt": "https://chat.openai.com"
}

def open_website(site_name):
    site_name = site_name.lower().strip()

    if site_name in SITES:
        webbrowser.open(SITES[site_name])
        print(f"Opening {site_name}")
    else:
        # fallback
        url = f"https://{site_name}.com"
        webbrowser.open(url)
        print(f"Opening {site_name}")