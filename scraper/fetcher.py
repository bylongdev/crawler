from .static_fetcher import fetch_static_html
from .dynamic_fetcher import fetch_dynamic_html
from extractor.contact_extractor import extract_contacts_from_html  # adjust path if needed
from urllib.parse import urlparse
import json

def load_cookies_from_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        raw = json.load(file)
        return {cookie["name"]: cookie["value"] for cookie in raw}

def fetch_html(url: str, cookie_path: str = "./scraper/cookies.json") -> tuple[str, str, list[dict]]:
    cookies = load_cookies_from_json(cookie_path)

    try:
        html = fetch_static_html(url, cookies=cookies)
        contacts = extract_contacts_from_html(html, url)

        if contacts: 
            print(f"✨ Emails found in static HTML! Using static mode.")
            return html, "static", contacts

        print("⚠️ No emails in static HTML. Falling back to dynamic fetch...")

        html = fetch_dynamic_html(url, cookies=cookies)
        contacts = extract_contacts_from_html(html, url)

        if contacts: 
            print(f"✨ Emails found in dynamic HTML! Using dynamic mode. {contacts}")
            return html, "dynamic", contacts
        else:
            print("⚠️ No emails found in dynamic HTML.")
            return html, "dynamic", []
        
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return html, "error", []
