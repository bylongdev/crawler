from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import time

class Browser:
  def __init__(self, wait_selector: str = "body", timeout: int = 10, headless: bool = False):
    self.wait_selector = wait_selector
    self.timeout = timeout

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--log-level=3")

    self.driver = webdriver.Chrome(options=options)

  def setup_driver(self, url: str, cookies: dict = None) -> webdriver.Chrome:
        driver = self.driver
        self._prepare_page(url, cookies)
        return self.driver

  def _prepare_page(self, url: str, cookies: dict = None):
    if cookies:
        self.driver.get(url)
        for name, value in cookies.items():
            self.driver.add_cookie({"name": name, "value": value})

    self.driver.get(url)
    self.wait_for_ready()
      

  def wait_for_ready(self):
      WebDriverWait(self.driver, self.timeout).until(
          lambda d: d.execute_script("return document.readyState") == "complete"
      )
      WebDriverWait(self.driver, self.timeout).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, self.wait_selector))
      )
      


  def close(self):
        self.driver.quit()

