import re
import time
from urllib.parse import urlparse
from .dynamic_fetcher import PersistentBrowser
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class GoogleMapsScraper(PersistentBrowser):
    def __init__(self):
        super().__init__()  # 💖 Call parent class constructor
        self.driver = self.setup_driver("https://www.google.com/maps")
        
    def search_business(self, business_url:str = "https://www.businesslocal.com.au", business_name:str = "Business Local Directory", location:str = "Melbourne") -> None:
        """
        Search for a business on Google Maps.
        """

        self._search_by_name(business_url, business_name, location)

        is_website_valid = self._validate_business_website(business_url)

        if is_website_valid:
            """ Start Gather Data:
            - phone number
            - address
            - google maps embed link
             """
            phone_number = self._get_phone_number()
            address = self._get_address()
            embed_map_link = self._get_embed_map_link()
            print(f"Phone number: {phone_number} \nAddress: {address} \nEmbed map link: {embed_map_link}")
            

        return self.driver.page_source if is_website_valid else None
    
    def _search_by_name(self, business_url:str, business_name:str, location:str) -> None:
        """
        Search for a business by url, name and location on Google Maps.
        """
        search_box = self.driver.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(f"{business_name} {business_url} {location}")
        search_box.send_keys(Keys.ENTER) 
        time.sleep(2)

        super().wait_for_ready()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-item-id='authority']"))
        )
        # return self.driver 
    
    def _get_website(self) -> str:
        """
        Get the website of the business.
        """
        try:
            link = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
            href = link.get_attribute("href")
            return href if href else ""
        except:
            pass
        return ""
    
    def _clean_website_url(self, url: str) -> str:
        if not url:
            return ""

        # Parse the URL and extract netloc (host/domain part)
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove 'www.' prefix if it exists
        domain = re.sub(r'^www\.', '', domain)

        return domain

    def _validate_business_website(self, expected_url: str) -> bool:
        actual_url = self._get_website()
    
        if not actual_url:
            print("❌ No website found.")
            return False

        if self._compare_websites(actual_url, expected_url):
            print(f"✅ Website matched: {actual_url}")
            return True
        else:
            print(f"❌ Website mismatch: {actual_url} ≠ {expected_url}")
            return False

    def _compare_websites(self, actual_url: str, expected_url: str) -> bool:
        actual = self._clean_website_url(actual_url)
        expected = self._clean_website_url(expected_url)
        
        return (
            actual == expected or
            actual.startswith(expected) or
            expected in actual
        )

    def _get_phone_number(self) -> str:
        selectors = [
            "button[data-item-id='phone:tel']",
            "button[aria-label*='Phone']",
            "button[aria-label*='phone']",
            "button[data-tooltip*='phone']",
            "div[data-item-id='phone:tel']",
        ]
        
        for selector in selectors:
            try:
                phone_el = self.driver.find_element(By.CSS_SELECTOR, selector)
                if phone_el.is_displayed():
                    full_phone = phone_el.text.strip()
                
                    # 🧹 Remove any weird leading symbols (like '')
                    cleaned = re.sub(r"^[^\w\d]+", "", full_phone)

                    return cleaned.strip()
            except:
                continue
        return "Not available"

    def _get_address(self) -> str:
        selectors = [
            "button[data-item-id='address']",
            "button[aria-label*='Address']",
            "button[aria-label*='address']",
            "button[data-tooltip='Copy address']",
            "div[data-item-id='address']"
        ]

        for selector in selectors:
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, selector)
                if el.is_displayed():
                    full_text = el.text.strip()

                    # 🧹 Remove any weird leading symbols (like '')
                    cleaned = re.sub(r"^[^\w\d]+", "", full_text)

                    return cleaned.strip()
            except:
                continue
        return "Not available"
    
    def _get_embed_map_link(self) -> str:
        try:
            wait = WebDriverWait(self.driver, self.timeout)

            # Step 1: Wait & Click Share button
            share_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Share']"))
            )
            share_button.click()
            print("📤 Clicked Share!")

            wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "button[aria-label='Embed a map']"))
            )

            # Step 2: Wait & Click Embed a map tab
            embed_tab = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Embed a map']"))
            )
            embed_tab.click()
            print("🗺️ Clicked Embed a map tab!")

            # Step 3: Wait for the input to appear
            iframe_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[jsaction='pane.embedMap.clickInput']"))
            )
            iframe_html = iframe_input.get_attribute("value")

            # Step 4: Extract iframe src
            match = re.search(r'src="([^"]+)"', iframe_html)
            if match:
                print("✅ Got embed link!")
                return match.group(1)
            else:
                print("⚠️ Found iframe input but couldn't extract src.")

        except Exception as e:
            print(f"❌ Failed to get embed map link: {e}")

        return "Not available"

