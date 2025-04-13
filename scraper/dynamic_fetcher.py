# Fetch with Selenium (for dynamic pages)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time

def fetch_dynamic_html(url: str, wait_selector: str = "body", timeout: int = 10, cookies: dict = None) -> str:
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)

        if cookies:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            driver.get(base_url)
            for name, value in cookies.items():
                driver.add_cookie({"name": name, "value": value})
            driver.get(url)

        # ✨ Wait until page is fully loaded AND body has content
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(3)  # ← this lets footer content render properly!


        return driver.page_source
    finally:
        driver.quit()
