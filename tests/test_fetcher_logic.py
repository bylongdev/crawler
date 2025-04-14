from unittest.mock import patch
from scraper.fetcher import HTMLFetcher


def test_fetcher_static_success():
    fetcher = HTMLFetcher()
    with patch("scraper.fetcher.fetch_static_html", return_value="<html>hi</html>"), \
         patch("extractor.contact_extractor.EmailsExtractor.extract_emails", return_value=[{"value": "a@b.com"}]):
        html, mode, contacts = fetcher.fetch("http://test.com")
        assert mode == "static"
        assert contacts[0]["value"] == "a@b.com"


def test_fetcher_fallback_to_dynamic():
    fetcher = HTMLFetcher()
    with patch("scraper.fetcher.fetch_static_html", return_value="<html>empty</html>"), \
         patch("extractor.contact_extractor.EmailsExtractor.extract_emails", side_effect=[[], [{"value": "b@site.com"}]]), \
         patch("scraper.fetcher.PersistentBrowser.fetch", return_value="<html>dynamic</html>"):
        html, mode, contacts = fetcher.fetch("http://test.com")
        assert mode == "dynamic"
        assert contacts[0]["value"] == "b@site.com"
