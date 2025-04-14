import csv
from pathlib import Path
from utils import save
import tempfile

def test_save_compact_recommendation_csv_creates_and_appends_correctly():
    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile = Path(tmpdir) / "test_compact.csv"
        
        # First save
        save.save_compact_recommendation_csv(
            site="example.com",
            recommended="best@example.com",
            email_scores=[("best@example.com", 0.95), ("meh@example.com", 0.5)],
            filename=str(tmpfile)
        )

        # Second save (update)
        save.save_compact_recommendation_csv(
            site="example.org",
            recommended="admin@example.org",
            email_scores=[("admin@example.org", 0.9)],
            filename=str(tmpfile)
        )

        # Read file to check
        with open(tmpfile, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        assert len(reader) == 2
        assert reader[0]["site"] == "example.com"
        assert reader[0]["recommended"] == "best@example.com"
        assert "best@example.com" in reader[0]["scored"]
        assert "meh@example.com" in reader[0]["scored"]

        assert reader[1]["site"] == "example.org"
        assert reader[1]["recommended"] == "admin@example.org"
