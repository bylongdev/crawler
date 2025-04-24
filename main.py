import sys
import io
import time
import concurrent.futures

from scraper.gmaps_scraper import GoogleMapsScraper
from scraper.web_scraper import EmailProcessor
from utils.save import BusinessContactSnapshot  # 📦 Save class


def run_email_scraper(site: str) -> str:
    """Runs email extraction logic."""
    email_scraper = EmailProcessor(site)
    return email_scraper.process_emails()


def run_gmaps_scraper(site: str) -> dict | None:
    """Runs Google Maps scraping logic."""
    gmaps_scraper = GoogleMapsScraper()
    return gmaps_scraper.search_business(site)


def run_scraper(site: str, use_multithread: bool = True):
    """
    Runs scraping for a single site, either sequentially or in parallel.

    Args:
        site (str): URL of the business to scrape.
        use_multithread (bool): Whether to run email + maps scraping in parallel.
    """
    start_time = time.time()
    print(f"🔍 Scraping: {site}\n")

    if use_multithread:
        # 🚀 Multithreaded: email + maps scrape in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_email = executor.submit(run_email_scraper, site)
            future_gmaps = executor.submit(run_gmaps_scraper, site)

            filtered_email = future_email.result()
            gmaps_result = future_gmaps.result()
    else:
        # 🐢 Sequential: email then maps
        filtered_email = run_email_scraper(site)
        gmaps_result = run_gmaps_scraper(site)

    if gmaps_result is None:
        print("❌ Failed to scrape Google Maps data.")
        sys.exit(1)

    # 💾 Save contact snapshot
    snapshot = BusinessContactSnapshot(
        email=filtered_email or "",
        phone=gmaps_result["phone_number"],
        address=gmaps_result["address"],
        embed_map_link=gmaps_result["embed_map_link"],
        hours=gmaps_result["opening_hours"]
    )
    snapshot.save(site)

    # 🖨️ Output results
    print(f"\n📧 Email: {filtered_email}")
    print(f"📞 Phone: {gmaps_result['phone_number']}")
    print(f"🏠 Address: {gmaps_result['address']}")
    print(f"🗺️ Embed Map: {gmaps_result['embed_map_link']}")
    print(f"\n⏰ Opening Hours:\n{gmaps_result['opening_hours']}")

    end_time = time.time()
    print(f"\n⏱️ Execution time: {end_time - start_time:.2f} seconds")
    print("✅ Process completed successfully.")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 🖥️ Site to scrape
    site = "https://www.businesslocal.com.au/"  # Example

    # 🔁 Set to False to run sequentially
    run_scraper(site, use_multithread=True)