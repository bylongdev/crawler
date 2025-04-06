# Wrapper to choose static or dynamic fetcher
from .static_fetcher import fetch_static_html
from .dynamic_fetcher import fetch_dynamic_html

def fetch_html(url: str) -> tuple[str, str]:
    html = fetch_static_html(url)
    if html:
        return html, "static"
    
    html = fetch_dynamic_html(url)
    return html, "dynamic"
