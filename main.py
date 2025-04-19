import sys
import io
import time

from scraper.gmaps_scraper import GoogleMapsScraper
from scraper.web_scraper import EmailProcessor
from utils.save import BusinessContactSnapshot  # 📦 Your contact-saving class

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

start_time = time.time()

# 💻 Site to scrape
# site = "https://www.duralpsychology.com.au/"
site = "https://www.businesslocal.com.au/"  # Example site

# ✉️ Step 1: Email filtering
email_scraper = EmailProcessor(site)
filtered_email = email_scraper.process_emails()

# 📍 Step 2: Scrape GMaps info
gmaps_scraper = GoogleMapsScraper()
gmaps_result = gmaps_scraper.search_business(site)  # pass site if needed for validation

# ✅ Step 3: Unpack results from GMaps
phone = gmaps_result.get("phone_number", "")
address = gmaps_result.get("address", "")
embed = gmaps_result.get("embed_map_link", "")
hours = gmaps_result.get("opening_hours", "")

if gmaps_result is None:
    print("❌ Failed to scrape Google Maps data.")
    sys.exit(1)

# 💾 Step 4: Save to CSV snapshot
snapshot = BusinessContactSnapshot(
    email=filtered_email or "",
    phone=phone,
    address=address,
    embed_map_link=embed,
    hours=hours
)
snapshot.save(site)

# 🖨️ Final print
print(f"\n📧 Email: {filtered_email}")
print(f"📞 Phone: {phone}")
print(f"🏠 Address: {address}")
print(f"🗺️ Embed Map: {embed}")
print(f"\n⏰ Opening Hours:\n{hours}")

end_time = time.time()
print(f"\n⏱️ Execution time: {end_time - start_time:.2f} seconds")
print("✅ Process completed successfully.")