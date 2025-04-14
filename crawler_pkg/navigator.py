from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from scraper.fetcher import HTMLFetcher

KEYWORDS = ["contact", "about", "support", "team", "help", "impressum"]
MAX_PAGES = 10

class EmailCrawler:
    def __init__(self, fetcher: HTMLFetcher = None):
        self.fetcher = fetcher or HTMLFetcher()
        self.visited = set()
        self.queue = []
        self.all_contacts = []

    def crawl(self, start_url: str) -> list[dict]:
        self.queue = [start_url]
        self.visited.clear()
        self.all_contacts.clear()

        base_domain = urlparse(start_url).netloc

        while self.queue and len(self.visited) < MAX_PAGES:
            url = self.queue.pop(0)
            if url in self.visited:
                continue

            print(f"🔎 Visiting: {url}")
            self.visited.add(url)

            try:
                html, mode, contacts = self.fetcher.fetch(url)
                print(f"Using mode: {mode}")
                self.all_contacts.extend(contacts)

                if "facebook.com" in urlparse(url).netloc and contacts:
                    print(f"✨ Found emails on Facebook page: {contacts}")
                    return contacts

                if "facebook.com" in urlparse(url).netloc:
                    continue  # Don't crawl deeper into Facebook

                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    text = a.get_text()
                    full_url = urljoin(url, href)

                    if full_url in self.visited:
                        continue

                    if (
                        self._is_internal_link(full_url, base_domain)
                        and self._is_useful_link(href + text)
                    ):
                        self.queue.append(full_url)

                    if self._is_social_media_link(full_url):
                        about_url = self._parse_link_to_about(full_url)
                        if about_url and about_url not in self.visited and about_url not in self.queue:
                            print(f"🌟 Prioritising Facebook About page: {about_url}")
                            self.queue.insert(0, about_url)


            except Exception as e:
                print(f"❌ Failed to process {url}: {e}")

        return self.all_contacts

    def _is_internal_link(self, link: str, base_domain: str) -> bool:
        parsed = urlparse(link)
        return parsed.netloc == "" or parsed.netloc == base_domain

    def _is_social_media_link(self, link: str) -> bool:
        return "facebook.com" in link

    def _parse_link_to_about(self, link: str) -> str | None:
        parsed = urlparse(link)
        if parsed.netloc == "":
            return None

        netloc = parsed.netloc.lower().replace("m.facebook", "www.facebook").replace("fb.com", "www.facebook.com")
        path_parts = parsed.path.strip("/").split("/")

        if not path_parts or path_parts[0] in ["", "about", "privacy", "support", "policies", "business", "careers"]:
            return None

        if path_parts[0] == "profile.php":
            query = parse_qs(parsed.query)
            user_id = query.get("id", [""])[0]
            if user_id:
                return f"https://{netloc}/profile.php?id={user_id}&sk=about"
            return None

        username = path_parts[0]
        return f"https://{netloc}/{username}/about"

    def _is_useful_link(self, link_text: str) -> bool:
        return any(keyword in link_text.lower() for keyword in KEYWORDS)
