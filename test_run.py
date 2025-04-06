from filter.mistral_filter import filter_emails_with_mistral
from crawler.navigator import crawl_for_emails

# ... after scraping
raw_emails = crawl_for_emails("https://longnguyen.tech")

print(f"\n📧 Raw emails found: {[e['value'] for e in raw_emails]}")

filtered = filter_emails_with_mistral(raw_emails)

print(f"\n🎯 Mistral-approved emails:")
for email in filtered:
    print(f" → {email}")
