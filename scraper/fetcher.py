import json
from urllib.parse import urlparse
from .static_fetcher import fetch_static_html
from .dynamic_fetcher import DynamicFetcher
from extractor.contact_extractor import EmailsExtractor


class HTMLFetcher:
    def __init__(self, cookie_path: str = "./scraper/cookies.json"):
        self.cookies = self.load_cookies_from_json(cookie_path)
        self.browser = DynamicFetcher()  # Keep browser alive for this instance
        self.extractor = EmailsExtractor()

    def load_cookies_from_json(self, path: str) -> dict:
        """
        Loads cookies from a JSON file and returns a name:value cookie dictionary.
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                raw = json.load(file)
                return {cookie["name"]: cookie["value"] for cookie in raw}
        except FileNotFoundError:
            print(f"⚠️ Cookie file not found at: {path}")
            return {}

    def fetch(self, url: str) -> tuple[str, str, list[dict]]:
        """
        Tries to fetch HTML content from a URL using static first, then dynamic if needed.

        Returns:
            - html (str): The page source
            - mode (str): "static", "dynamic", or "error"
            - contacts (list[dict]): List of extracted email contacts
        """
        try:
            # 🍃 Try static first
            html = fetch_static_html(url, cookies=self.cookies)
            contacts = self.extractor.extract_emails(html, url)

            if contacts:
                print(f"✨ Emails found in static HTML! Using static mode.")
                return html, "static", contacts

            print("⚠️ No emails in static HTML. Falling back to dynamic fetch...")

            # ⚡ Then try dynamic with persistent browser
            html = self.browser.fetch(url, cookies=self.cookies)
            contacts = self.extractor.extract_emails(html, url)

            if contacts:
                print(f"✨ Emails found in dynamic HTML! Using dynamic mode. {contacts}")
                return html, "dynamic", contacts

            print("⚠️ No emails found in dynamic HTML.")
            return html, "dynamic", []

        except Exception as e:
            print(f"❌ Error while fetching {url}: {e}")
            return "", "error", []

    def close(self):
        """Shuts down the persistent browser when finished."""
        self.browser.close()
