import csv
from pathlib import Path


def save_compact_recommendation_csv(
    site: str,
    recommended: str,
    email_scores: list[tuple[str, float]],
    filename: str = "compact_recommendations.csv"
) -> str:
    """
    Saves a compact CSV with one row per site including recommended email and list of scored emails (no scores shown).
    """

    filepath = Path(filename)
    rows = {}

    # Load previous data
    if filepath.exists():
        with open(filepath, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows[row["site"]] = {
                    "recommended": row["recommended"],
                    "scored": row["scored"]
                }

    # Format email list (just emails, no scores)
    email_list_str = "; ".join(
        email.strip().lower()
        for email, _ in sorted(email_scores, key=lambda x: -x[1])
    )

    # Update row
    rows[site] = {
        "recommended": recommended,
        "scored": email_list_str
    }

    # Save updated
    with open(filepath, mode="w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["site", "recommended", "scored"])
        for site, data in rows.items():
            writer.writerow([site, data["recommended"], data["scored"]])

    print(f"📦 Saved compact CSV (emails only) to: {filepath}")
    return str(filepath)
