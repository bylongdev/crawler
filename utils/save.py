from pathlib import Path
from datetime import datetime
import csv

class BusinessContactSnapshot:
    def __init__(
        self,
        email: str,
        phone: str,
        address: str,
        embed_map_link: str,
        hours: str = "",
        filename: str = "business_contacts.csv"
    ):
        self.email = email
        self.phone = phone
        self.address = address
        self.embed_map_link = embed_map_link
        self.hours = hours
        self.filepath = Path(filename)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not self.filepath.exists():
            with open(self.filepath, mode="w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "site", "email", "phone", "address", "embed_map_link", "hours", "timestamp"
                ])

    def save(self, site: str, timestamp: str = None) -> str:
        if not timestamp:
            timestamp = datetime.now().isoformat(timespec='seconds')

        with open(self.filepath, mode="a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                site,
                self.email,
                self.phone,
                self.address,
                self.embed_map_link,
                self.hours,
                timestamp
            ])

        print(f"💾 Saved business contact for {site} at {timestamp}")
        return str(self.filepath)
