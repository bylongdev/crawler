# dynamic_fetcher.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import time

from scraper.browser import Browser

class DynamicFetcher(Browser):
    def __init__(self, wait_selector: str = "body", timeout: int = 10, headless: bool = False):
        super().__init__()

    def fetch(self, url: str, cookies: dict = None) -> str:
        driver = self.driver

        self._prepare_page(url, cookies)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        return driver.page_source

