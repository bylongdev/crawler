import re
from bs4 import BeautifulSoup

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
MAX_EMAIL_RESULTS = 10

def extract_contacts_from_html(html: str, source_url: str = "") -> list[dict]:
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")

    found_contacts = []
    seen_emails = set()

    # ✨ 1. Search in plain text
    for match in EMAIL_REGEX.findall(text):
        clean = match.lower()
        if clean not in seen_emails:
            seen_emails.add(clean)
            found_contacts.append({
                "type": "email",
                "value": clean,
                "source": source_url,
                "context": "page_text"
            })
        if len(seen_emails) >= MAX_EMAIL_RESULTS:
            return found_contacts

    # ✨ 2. Search in `href="mailto:..."` attributes
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.lower().startswith("mailto:"):
            email = href.split("mailto:")[1].split("?")[0].strip().lower()
            if email and email not in seen_emails:
                seen_emails.add(email)
                found_contacts.append({
                    "type": "email",
                    "value": email,
                    "source": source_url,
                    "context": "mailto"
                })
            if len(seen_emails) >= MAX_EMAIL_RESULTS:
                break

    return found_contacts
