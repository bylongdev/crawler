# Fetch with Selenium (for dynamic pages)
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def fetch_dynamic_html(url: str, wait_time: float = 3.0) -> str:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1920x1080")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(wait_time)
        html = driver.page_source
    finally:
        driver.quit()
    return html
