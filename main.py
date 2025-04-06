from scraper.fetcher import fetch_html

url = "https://example.com"
html, mode = fetch_html(url)

print(f"[+] Page loaded using {mode} mode.")
