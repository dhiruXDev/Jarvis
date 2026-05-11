from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse


def play_song(song_name):
    try:
        options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(options=options)

        query = urllib.parse.quote(song_name)

        url = (
            "https://www.youtube.com/results?"
            f"search_query={query}"
        )

        driver.get(url)

        # WAIT until video appears
        first_video = WebDriverWait(
            driver,
            15
        ).until(
            EC.element_to_be_clickable(
                (By.ID, "video-title")
            )
        )

        # CLICK first video
        first_video.click()

        return f"Playing {song_name}"

    except Exception as e:

        print(f"Play Song Error: {e}")

        return "Unable to play song"