# crawler/navigator.py
from urllib.parse import urljoin, urlparse
from scraper.fetcher import fetch_html
from extractor.contact_extractor import extract_contacts_from_html
from bs4 import BeautifulSoup

# Keywords that often lead to contact info
KEYWORDS = ["contact", "about", "support", "team", "help", "impressum"]

MAX_PAGES = 3  # Limit how deep we go

def is_internal_link(link: str, base_domain: str) -> bool:
    parsed = urlparse(link)
    return parsed.netloc == "" or parsed.netloc == base_domain

def is_useful_link(link_text: str) -> bool:
    return any(keyword in link_text.lower() for keyword in KEYWORDS)

def crawl_for_emails(start_url: str) -> list[dict]:
    visited = set()
    queue = [start_url]
    all_contacts = []

    base_domain = urlparse(start_url).netloc

    while queue and len(visited) < MAX_PAGES:
        url = queue.pop(0)
        if url in visited:
            continue

        print(f"🔎 Visiting: {url}")
        visited.add(url)

        try:
            html, mode = fetch_html(url)
            contacts = extract_contacts_from_html(html, source_url=url)
            all_contacts.extend(contacts)

            # Only parse links from this page if needed
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text()

                full_url = urljoin(url, href)

                if (
                    is_internal_link(full_url, base_domain)
                    and is_useful_link(href + text)
                    and full_url not in visited
                ):
                    queue.append(full_url)

        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")

    return all_contacts
