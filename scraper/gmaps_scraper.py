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
        
    def search_business(self, business_url: str = "https://www.businesslocal.com.au", business_name: str = "Business Local", location: str = "Melbourne") -> dict | None:
        """
        Search and extract business info from Google Maps, even if multiple results appear.
        """
        print(f"🔍 Searching for: {business_name} in {location}")
        self._search_by_name(business_name, location)

        print("🔗 Validating website...")

        # If already on business page
        if "/maps/place/" in self.driver.current_url:
            print("📍 Landed directly on business page!")
            if self._validate_business_website(business_url):
                return self._extract_all_info()
            else:
                print("❌ Website validation failed on direct page.")
                return None
            
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='Nv2PK']"))
        )

        
        # Else, check result list
        results = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='Nv2PK']")
        print(f"🗂️ Found {len(results)} search results. Checking up to 4...")

        for idx, result in enumerate(results[:10]):
            print(f"\n🧪 Checking result {idx+1}...")

            # 🚫 Skip if sponsored
            if self._is_sponsored_result(result):
                print("🚫 Skipping sponsored result.")
                continue

            try:
                link = result.find_element(By.CSS_SELECTOR, "a.hfpxzc")
                self.driver.execute_script("arguments[0].click();", link)

                # 🏷️ Print out the business name
                business_label = link.get_attribute("aria-label")
                print(f"🔖 Business name: {business_label}")

                # time.sleep(1)  # Wait for the page to load
                super().wait_for_ready()
                # WebDriverWait(self.driver, self.timeout).until( 
                #     EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-item-id='authority']"))
                # )

                if self._validate_business_website(business_url):
                    href = link.get_attribute("href")
                    self.driver.get(href)  # Go back to the original page

                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-item-id='authority']"))
                    )
                    
                    print("✅ Matched result!")
                    print(self._extract_all_info())
                    return None

                print("⏪ Going back to results...")
                # self.driver.back()
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='Nv2PK']"))
                )

            except Exception as e:
                print(f"⚠️ Error clicking result {idx+1}: {e}")
                continue

        print("❌ No matching result found.")
        return None

    def _extract_all_info(self) -> dict:
        """Extracts all available business contact details."""
        phone_number = self._get_phone_number()
        address = self._get_address()
        embed_map_link = self._get_embed_map_link()
        opening_hours = self._get_opening_hours()

        return {
            "phone_number": phone_number,
            "address": address,
            "embed_map_link": embed_map_link,
            "opening_hours": opening_hours
        }

    
    def _search_by_name(self, business_name:str, location:str) -> None:
        """
        Search for a business by url, name and location on Google Maps.
        """
        search_box = self.driver.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(f"{business_name} {location}")
        search_box.send_keys(Keys.ENTER) 
        time.sleep(2)

        super().wait_for_ready()

        # WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-item-id='authority']"))
        # )
    
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
        
    def _is_sponsored_result(self, element) -> bool:
        """
        Detect if a result is sponsored based on keywords and class hints.
        """
        try:
            # Check for known sponsored words
            text = element.text.lower()
            if "sponsored" in text:
                return True

            # Check for class-based hints (can be obfuscated)
            class_attr = element.get_attribute("class") or ""
            if "ad" in class_attr.lower():
                return True

            return False
        except:
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
    
    def _get_opening_hours(self) -> str:
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, "div[aria-label*='day']")
            raw = el.get_attribute("aria-label")

            if raw:
                cleaned_lines = []
                for part in raw.split(";"):
                    if any(day in part for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                        # Clean up display string
                        line = re.sub(r"\(.*?\)", "", part)  # Remove (Holiday Notes)
                        line = re.sub(r"Hours might differ", "", line, flags=re.IGNORECASE)
                        line = line.replace("Hide opening hours for the week", "")
                        line = re.sub(r"\s+", " ", line).strip()

                        # 👉 Only now: split by comma THEN clean symbols!
                        if "," in line:
                            day, *hours = line.split(",", 1)
                            day = day.strip().replace(",", "").replace(".", "")
                            hours = hours[0].strip().replace(",", "").replace(".", "")
                            cleaned_lines.append(f"{day}: {hours}")

                return "\n".join(cleaned_lines)

        except Exception as e:
            print(f"❌ Failed to get weekly hours: {e}")

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
            embed_tab = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Embed a map']"))
            )

            time.sleep(1)  # Wait for the iframe to load

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

