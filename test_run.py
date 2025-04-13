from filter.mistral_filter import filter_emails_with_mistral
from crawler.navigator import crawl_for_emails
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ... after scraping
site = "https://longnguyen.tech/"
# site = "https://www.replicafurniture.com.au/"
raw_emails = crawl_for_emails(site)

print(f"\n📧 Raw emails found: {[e['value'] for e in raw_emails]}")

if not raw_emails:
    print("😢 No emails found to evaluate. Skipping Mistral...")
else:
    filtered = filter_emails_with_mistral(raw_emails)

    print(f"\n🎯 Mistral-approved emails:")
    for email in filtered:
        print(f" → {email}")


