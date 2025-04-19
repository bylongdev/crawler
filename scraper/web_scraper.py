from filter.mistral_filter import MistralEmailFilter
from crawler_pkg.navigator import EmailCrawler
import sys
import io


class EmailProcessor:
    def __init__(self, site: str):
        self.site = site
        self.crawler = EmailCrawler()
        self.mistral_filter = MistralEmailFilter()

    def process_emails(self) -> dict:
        """
        Crawl and filter emails using Mistral.
        Returns:
            dict: {
                'site': str,
                'raw_emails': list[str],
                'recommended': str or None
            }
        """
        raw_results = self.crawler.crawl(self.site)
        raw_emails = [e['value'] for e in raw_results]
        filtered_email = None

        print(f"\n📧 Raw emails found: {raw_emails}")

        if not raw_emails:
            print("😢 No emails found to evaluate. Skipping Mistral...")
        else:
            filtered_email = self.mistral_filter.filter(raw_results)
            print(f"\n🎯 Mistral-approved email: {filtered_email}")

        return filtered_email
