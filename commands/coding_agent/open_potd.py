# pyrefly: ignore [missing-import]
from playwright.sync_api import sync_playwright

import subprocess
import time
import urllib.request
import urllib.error

def open_leetcode_potd():
    p = sync_playwright().start()

    user_data_dir = r"C:\Users\utkar\AppData\Local\Google\Chrome\User Data"
    profile = "Profile 9"
    port = 9222
    
    # Check if Chrome with remote debugging is already running on port 9222
    try:
        urllib.request.urlopen(f"http://localhost:{port}/json/version", timeout=1)
    except urllib.error.URLError:
        # Launch Chrome via subprocess detached
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        try:
            subprocess.Popen([
                chrome_path,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={user_data_dir}",
                f"--profile-directory={profile}",
                "--no-sandbox"
            ])
            time.sleep(2)  # Give Chrome a couple of seconds to start up
        except Exception as e:
            print(f"Failed to launch Chrome via subprocess: {e}")
            raise e

    try:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")
    except Exception as e:
        print("Failed to connect to Chrome CDP. Make sure Chrome is running with remote debugging enabled.")
        raise e


    page = browser.new_page()

    page.goto(
        "https://leetcode.com/problemset/all"
    )
    print("LeetCode opened")
    return page, browser, p