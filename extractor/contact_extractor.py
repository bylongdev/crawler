import re
from bs4 import BeautifulSoup

class EmailsExtractor:
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    MAX_EMAIL_RESULTS = 10

    def __init__(self, max_results: int = 10):
        self.max_results = max_results

    def clean_email(self, email: str) -> str:
        return email.split("?")[0].strip().lower()

    def extract_emails(self, html: str, source_url: str = "") -> list[dict]:
        """
        Extracts emails from HTML content including page text and mailto: links.

        Returns a list of dictionaries with:
        - type
        - value
        - source
        - context
        """
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ")

        found_contacts = []
        seen_emails = set()

        # ✨ 1. Search in plain text
        for match in self.EMAIL_REGEX.findall(text):
            email = self.clean_email(match)
            if email not in seen_emails:
                seen_emails.add(email)
                found_contacts.append({
                    "type": "email",
                    "value": email,
                    "source": source_url,
                    "context": "page_text"
                })
            if len(seen_emails) >= self.max_results:
                return found_contacts

        # ✨ 2. Search in mailto: links
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            if href.lower().startswith("mailto:"):
                email = self.clean_email(href.split("mailto:")[1])
                if email and email not in seen_emails:
                    seen_emails.add(email)
                    found_contacts.append({
                        "type": "email",
                        "value": email,
                        "source": source_url,
                        "context": "mailto"
                    })
                if len(seen_emails) >= self.max_results:
                    break

        return found_contacts
