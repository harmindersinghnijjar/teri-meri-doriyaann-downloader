import datetime
import json
import logging
import os
import time
from urllib import response
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading

# Setup Logging
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("teri-meri-doriyaann-downloader.log", mode="a")
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)s] [%(pathname)s:%(lineno)d] - %(message)s - [%(process)d:%(thread)d]"
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

# Selenium Automation
class SeleniumAutomation:
    def __init__(self, driver):
        self.driver = driver

    def open_target_page(self, url):
        self.driver.get(url)
        time.sleep(5)

    def extract_video_links(self):
        results = {"videos": []}
        try:
            # Current date in the desired format DD-Month-YYYY
            current_date = datetime.datetime.now().strftime("%d-%B-%Y")

            link_selector = f'//*[@id="content"]/div[5]/article[1]/div[2]/span/h2/a'
            if WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, link_selector))
            ):
                self.driver.find_element(By.XPATH, link_selector).click()
                time.sleep(30)  # Adjust the timing as needed

                first_video_player = "/html/body/div[1]/div[2]/div/div/div[1]/div/article/div[3]/center/div/p[14]/a"
                second_video_player = "/html/body/div[1]/div[2]/div/div/div[1]/div/article/div[3]/center/div/p[12]/a"

                for player in [first_video_player, second_video_player]:
                    if WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, player))
                    ):
                        self.driver.find_element(By.XPATH, player).click()
                        time.sleep(10)  # Adjust the timing as needed
                        # Switch to the new tab that contains the video player
                        self.driver.switch_to.window(self.driver.window_handles[1])
                        elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
                        for element in elements:
                            if element.tag_name == "iframe" and element.get_attribute("src"):
                                logger.info(f"Element: {element.get_attribute('outerHTML')}")
                                try:
                                    video_url = element.get_attribute("src")
                                except Exception as e:
                                    logger.error(f"Error getting video URL: {e}")
                                    continue

                                self.driver.get(video_url)
                                elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
                                for element in elements:
                                    if element.tag_name == "video" and element.get_attribute("src") and element.get_attribute("src").endswith(".mp4"):
                                        logger.info(f"Element: {element.get_attribute('outerHTML')}")
                                        try:
                                            video_url = element.get_attribute("src")
                                        except Exception as e:
                                            logger.error(f"Error getting video URL: {e}")
                                            continue

                                        logger.info(f"Video URL: {video_url}")
                                        video_name = video_url.split("/")[-1]
                                        logger.info(f"Video Name: {video_name}")
                                        response = requests.get(video_url, stream=True)
                                        with open(
                                            f"E:/Plex/Teri Meri Doriyaann/{current_date}.mp4",
                                            "wb",
                                        ) as file:
                                            for chunk in response.iter_content(chunk_size=1024):
                                                print(f"Writing chunk {chunk}")
                                                # writing one chunk at a time to pdf file
                                                if chunk:
                                                    file.write(chunk)
                                                    print(f"Chunk {chunk} written")
                                        logger.info(f"Video {video_name} saved successfully")
                                        break
        except Exception as e:
            logger.error(f"Error in extract_video_links: {e}")

    def close_browser(self):
        self.driver.quit()


# Video Scraper
class VideoScraper:
    def __init__(self):
        self.user = os.getlogin()
        self.selenium = None

    def setup_driver(self):
        # Set up ChromeDriver service
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir=C:\\Users\\{self.user}\\AppData\\Local\\Google\\Chrome\\User Data")
        options.add_argument("--profile-directory=Default")
        return webdriver.Chrome(service=service, options=options)

    def start_scraping(self):
        try:
            self.selenium = SeleniumAutomation(self.setup_driver())
            self.selenium.open_target_page("https://www.desi-serials.cc/watch-online/star-plus/teri-meri-doriyaann/")
            videos = self.selenium.extract_video_links()
            self.save_videos(videos)
        finally:
            if self.selenium:
                self.selenium.close_browser()

    def save_videos(self, videos):
        with open("desi_serials_videos.json", "w", encoding="utf-8") as file:
            json.dump(videos, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    os.system("taskkill /im chrome.exe /f")
    scraper = VideoScraper()
    scraper.start_scraping()
