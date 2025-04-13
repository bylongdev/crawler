# Fetch with requests (for static pages)
import requests

def fetch_static_html(url: str, timeout: int = 10, cookies: dict = None) -> str | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
        if response.ok and "text/html" in response.headers.get("Content-Type", ""):
            return response.text
    except requests.RequestException:
        return None
