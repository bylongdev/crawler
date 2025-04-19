from filter.mistral_filter import MistralEmailFilter
from crawler_pkg.navigator import EmailCrawler
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

start_time = time.time()

# ... after scraping
# site = "https://longnguyen.tech/"
# site = "https://www.duralpsychology.com.au/"
site = "https://possumranger.com.au/"
crawler = EmailCrawler()
raw_emails = crawler.crawl(site)
Mistral = MistralEmailFilter()
filtered_email = ""

print(f"\n📧 Raw emails found: {[e['value'] for e in raw_emails]}")

if not raw_emails:
    print("😢 No emails found to evaluate. Skipping Mistral...")
else:
    filtered_email = Mistral.filter(raw_emails)

    print(f"\n🎯 Mistral-approved emails:")
    # for email in filtered:
    print(f" → {filtered_email}")


end_time = time.time()
execution_time = end_time - start_time  
print(f"\nExecution time: {execution_time:.2f} seconds")
