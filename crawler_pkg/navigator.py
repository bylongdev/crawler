# crawler/navigator.py
from urllib.parse import urljoin, urlparse
from scraper.fetcher import fetch_html
from extractor.contact_extractor import extract_contacts_from_html
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, parse_qs

# Keywords that often lead to contact info
KEYWORDS = ["contact", "about", "support", "team", "help", "impressum"]

MAX_PAGES = 10  # Limit how deep we go

def is_internal_link(link: str, base_domain: str) -> bool:
    parsed = urlparse(link)
    return parsed.netloc == "" or parsed.netloc == base_domain

def is_social_media_link(link: str ) -> bool:
    social_media_domains = [
        "facebook.com"
        # , "twitter.com", "linkedin.com",
        # "instagram.com", "youtube.com", "pinterest.com",
        # "tiktok.com", "snapchat.com", "reddit.com"
    ]
    return any(domain in link for domain in social_media_domains)

def parse_link_to_about(link: str) -> str | None:
    parsed = urlparse(link)

    if parsed.netloc == "":
        return None

    # Normalise the domain
    netloc = parsed.netloc.lower()
    if "facebook" not in netloc:
        return None

    netloc = netloc.replace("m.facebook", "www.facebook").replace("fb.com", "www.facebook.com")
    path_parts = parsed.path.strip("/").split("/")

    # Reject if it's generic or weird
    if not path_parts or path_parts[0] in ["", "about", "privacy", "support", "policies", "business", "careers"]:
        return None

    # Handle profile.php?id=... pattern
    if path_parts[0] == "profile.php":
        query = parse_qs(parsed.query)
        user_id = query.get("id", [""])[0]
        if user_id:
            return f"https://{netloc}/profile.php?id={user_id}&sk=about"
        return None

    # Assume it's a username/page name
    username = path_parts[0]
    return f"https://{netloc}/{username}/about"


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
            html, mode, contacts = fetch_html(url)

            print(f"Using mode: {mode}")
            all_contacts.extend(contacts)

            if "facebook.com" in urlparse(url).netloc and len(contacts) > 0:
                print(f"✨ Found emails on Facebook page: {contacts}")
                return contacts

            # 💣 Stop crawling links if we're already inside Facebook
            if "facebook.com" in urlparse(url).netloc:
                continue  # do not parse any more links from inside Facebook!

            soup = BeautifulSoup(html, "html.parser")
            
            # Extract all links on the page
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text()
                full_url = urljoin(url, href)

                if full_url in visited:
                    continue

                if (
                    is_internal_link(full_url, base_domain)
                    and is_useful_link(href + text)
                    and full_url not in visited
                ):
                    queue.append(full_url)



                # 💙 Prioritise Facebook About links
                if is_social_media_link(full_url):
                    about_url = parse_link_to_about(full_url)
                    if about_url and about_url not in visited:
                        print(f"🌟 Prioritising Facebook About page: {about_url}")
                        queue.insert(0, about_url)
                    continue


        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")

    return all_contacts
