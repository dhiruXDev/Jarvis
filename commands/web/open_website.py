import webbrowser
import re

# Known websites
SITES = {
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "leetcode": "https://leetcode.com",
    "chatgpt": "https://chat.openai.com",
    "google": "https://google.com",
    "reddit": "https://reddit.com",
    "linkedin": "https://linkedin.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "instagram": "https://instagram.com",
    "facebook": "https://facebook.com"
}

def open_website(site_name):

    try:

        site_name = site_name.lower().strip()

        # Remove extra spaces
        site_name = re.sub(r"\s+", " ", site_name)

        print(f"[OPEN WEBSITE] Requested: {site_name}")

        # =========================
        # PREDEFINED SITES
        # =========================
        if site_name in SITES:

            url = SITES[site_name]

            webbrowser.open(url)

            print(f"[OPEN WEBSITE] Opening predefined: {url}")

            return f"Opening {site_name}"

        # =========================
        # IF USER GIVES FULL URL
        # =========================
        if site_name.startswith("http://") or site_name.startswith("https://"):

            webbrowser.open(site_name)

            print(f"[OPEN WEBSITE] Opening direct URL")

            return f"Opening {site_name}"

        # =========================
        # REMOVE SPACES
        # stack overflow -> stackoverflow
        # =========================
        clean_name = site_name.replace(" ", "")

        # =========================
        # GENERIC DOMAIN
        # =========================
        url = f"https://{clean_name}.com"

        webbrowser.open(url)

        print(f"[OPEN WEBSITE] Opening generic URL: {url}")

        return f"Opening {site_name}"

    except Exception as e:

        print(f"[OPEN WEBSITE ERROR] {e}")

        return "Unable to open website"