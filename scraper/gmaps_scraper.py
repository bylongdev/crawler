from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, quote_plus
import time

class GoogleMapsScraper:
    def __init__(self, browser):
        self.browser = browser  # 🧠 Pass in the shared PersistentBrowser instance

    def search(self, keyword: str):
        """Open a search result in Google Maps for the given keyword."""
        query = quote_plus(keyword)
        url = f"https://www.google.com/maps/search/{query}/"
        print(f"🔍 Searching GMaps for: {keyword}")
        self.browser.driver.get(url)
        time.sleep(4)

        # Wait until listings are loaded
        WebDriverWait(self.browser.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[role="article"]'))
        )

    def get_listings(self, max_results: int = 10) -> list[dict]:
        """Extracts top search result cards from GMaps."""
        print("📦 Extracting business listing previews...")
        listings = self.browser.driver.find_elements(By.CSS_SELECTOR, '[role="article"]')

        results = []
        for listing in listings[:max_results]:
            try:
                name = listing.find_element(By.CSS_SELECTOR, 'h3 span').text
                link_elem = listing.find_element(By.CSS_SELECTOR, 'a')
                href = link_elem.get_attribute("href")

                results.append({
                    "name": name,
                    "gmaps_link": href
                })
                print(f"🏪 {name} → {href}")
            except Exception as e:
                print("❌ Skipped one listing:", e)

        return results

    def get_listing_details(self, listing_url: str) -> dict:
        """Open an individual listing and extract detail info (address, website, etc)."""
        print(f"🧭 Visiting listing detail: {listing_url}")
        self.browser.driver.get(listing_url)
        time.sleep(3)

        details = {}

        try:
            details["name"] = self.browser.driver.find_element(By.CSS_SELECTOR, "h1 span").text
        except:
            details["name"] = "N/A"

        try:
            website_button = self.browser.driver.find_element(By.XPATH, '//a[contains(@aria-label,"Website")]')
            details["website"] = website_button.get_attribute("href")
        except:
            details["website"] = None

        try:
            category = self.browser.driver.find_element(By.CSS_SELECTOR, '[jsaction*="pane.rating.category"]').text
            details["category"] = category
        except:
            details["category"] = "N/A"

        try:
            address = self.browser.driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]').text
            details["address"] = address
        except:
            details["address"] = "N/A"

        return details
