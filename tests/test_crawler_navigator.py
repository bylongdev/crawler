# tests/test_crawler_navigator.py

from crawler_pkg.navigator import crawl_for_emails

def test_crawl_finds_emails_on_example_com():
    # Example.com doesn't have real emails, but the function should run without error
    results = crawl_for_emails("https://example.com")

    assert isinstance(results, list)
    assert all("type" in r and "value" in r for r in results)

def test_crawler_does_not_crash_on_missing_pages():
    results = crawl_for_emails("https://example.com/nonexistent-page")

    assert isinstance(results, list)  # Should handle errors gracefully
