from .static_fetcher import fetch_static_html
from .dynamic_fetcher import fetch_dynamic_html
from extractor.contact_extractor import extract_contacts_from_html  # adjust path if needed

def fetch_html(url: str) -> tuple[str, str]:
    html = fetch_static_html(url)
    contacts = extract_contacts_from_html(html, url)

    if contacts:
        print(f"✨ Emails found in static HTML! Using static mode.")
        return html, "static"

    print("⚠️ No emails in static HTML. Falling back to dynamic fetch...")
    html = fetch_dynamic_html(url)
    return html, "dynamic"
