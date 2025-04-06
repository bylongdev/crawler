import re
from bs4 import BeautifulSoup

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
MAX_EMAIL_RESULTS = 10

def extract_contacts_from_html(html: str, source_url: str = "") -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")

    found_contacts = []
    seen_emails = set()

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
                break

    return found_contacts
