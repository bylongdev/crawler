import pytest
from unittest.mock import patch
from scraper import fetcher

def test_fetcher_static_success():
    with patch("scraper.fetcher.fetch_static_html", return_value="<html>hi</html>"), \
         patch("scraper.fetcher.extract_contacts_from_html", return_value=["a@b.com"]):
        html, mode, contacts = fetcher.fetch_html("http://test.com")

        assert mode == "static"
        assert "<html>" in html


def test_fetcher_fallback_to_dynamic():
    with patch("scraper.fetcher.fetch_static_html", return_value="<html>empty</html>"), \
         patch("scraper.fetcher.extract_contacts_from_html", return_value=[]), \
         patch("scraper.fetcher.fetch_dynamic_html", return_value="<html>dynamic</html>"):
        html, mode, contacts = fetcher.fetch_html("http://test.com")

        assert mode == "dynamic"
        assert "dynamic" in html
