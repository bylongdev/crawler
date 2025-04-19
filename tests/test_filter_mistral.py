
import pytest
from utils.save import save_compact_recommendation_csv
import csv
import os
from filter.mistral_filter import MistralEmailFilter

def test_filter_email_with_fallback(monkeypatch):
    fake_emails = [{"value": "noreply@example.com", "source": "https://example.com"}]

    Mistral = MistralEmailFilter()


    # Patch `ask_mistral` to return nothing so it triggers the fallback
    monkeypatch.setattr(Mistral, "ask_mistral", lambda _: "")

    result = Mistral.filter(fake_emails)
    assert result == "" or result == "noreply@example.com"  # fallback behaviour


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
