
import pytest
from filter.mistral_filter import filter_emails_with_mistral
from utils.save import save_compact_recommendation_csv
import csv
import os

def test_filter_email_with_fallback(monkeypatch):
    fake_emails = [{"value": "noreply@example.com", "source": "https://example.com"}]

    # Monkeypatch ask_mistral to simulate no valid output
    monkeypatch.setattr("filter.mistral_filter", "ask_mistral", lambda _: "")

    result = filter_emails_with_mistral(fake_emails)

    assert isinstance(result, list)
    assert result[0] == "noreply@example.com"  # fallback should still return something

def test_compact_csv_saved(tmp_path):
    from utils.save import save_compact_recommendation_csv

    file = tmp_path / "test_compact.csv"

    save_compact_recommendation_csv(
        site="testsite.com",
        recommended="contact@testsite.com",
        email_scores=[
            ("contact@testsite.com", 1.0),
            ("info@testsite.com", 0.5),
        ],
        filename=str(file)
    )

    with open(file, newline="") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 1
        assert reader[0]["site"] == "testsite.com"
        assert reader[0]["recommended"] == "contact@testsite.com"
        assert "contact@testsite.com" in reader[0]["scored"]
        assert "info@testsite.com" in reader[0]["scored"]
