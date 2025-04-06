# tests/test_static_fetcher.py
import re
from scraper.static_fetcher import fetch_static_html

def test_fetch_static_html_returns_html():
    url = "https://example.com"
    html = fetch_static_html(url)
    
    assert html is not None, "HTML content should not be None"
    assert "<html>" in html.lower(), "HTML should contain <html> tag"

def test_fetch_static_html_contains_title():
    url = "https://example.com"
    html = fetch_static_html(url)

    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    assert title_match is not None, "HTML should contain a <title> tag"

