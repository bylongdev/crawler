# filter/mistral_filter.py

import subprocess
from urllib.parse import urlparse

def ask_mistral(prompt: str) -> str:
    """Send a prompt to Ollama (Mistral) and return the output"""
    result = subprocess.run(
        ["ollama", "run", "mistral:latest", prompt],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def build_prompt(site: str, emails: list[str]) -> str:
    return f"""
You are a website contact email validator.

Official website: {site}

Below is a list of email addresses scraped directly from pages on this site:
{chr(10).join(emails)}

Your task is to choose the most likely contact email from this list.

Rules:
- ONLY choose from the emails in the list above. DO NOT make up or guess.
- Reply with just one email address only — no punctuation, no quotes, no commentary.
- Prefer emails that match the website domain.
- Prefer emails that are friendly and personal, like hello@ or contact@.
- Avoid generic or automated emails (like noreply@, info@, etc.).
- Avoid emails that look like placeholders or are malformed.
- Do not include duplicates or any email with subject/query parameters.
- Only return a real, valid email from the list.
- If there is no valid business contact email, return an empty string (nothing).

Return only the email address on a single line.

Additionally, include a score (between 0.0 and 1.0) for each email in this format:
email@example.com: 0.85
The scores should reflect how suitable each email is as a business contact.
""".strip()


def filter_emails_with_mistral(raw_emails: list[dict]) -> list[str]:
    if not raw_emails:
        return []

    # Extract raw list
    email_list = [email['value'].strip().lower() for email in raw_emails]
    test_emails = [
    "contact@longnguyen.tech",        # ✅ Official, matches domain, ideal
    "hello@longnguyen.tech",          # ✅ Friendly and matching domain
    "support@longnguyen.tech",        # ✅ Domain match, but a bit generic
    "admin@longnguyen.tech",          # ⚠️ Domain match, but generic/admin
    "team@longnguyen.tech",           # ✅ Decent, matching domain
    "info@longnguyen.tech",           # ⚠️ Common catch-all
    "noreply@longnguyen.tech",        # ❌ Bad for contacting
    "philong170101@gmail.com",        # ⚠️ Personal but real
    "contact.longnguyen@gmail.com",   # ⚠️ Business-y personal (less ideal)
    "noreply@mailer.example.com",     # ❌ Automatic / bulk email
    "test@email.com",                 # ❌ Looks fake or placeholder
    "abc@123.com",                    # ❌ Malformed or suspicious
    "ceo@longnguyen.tech",            # ✅ Rare but might be useful
    "marketing@longnguyen.tech",      # ✅ Depends on use case
]
    site_url = raw_emails[0]['source']
    domain = urlparse(site_url).netloc.replace("www.", "")

    # Build prompt and get Mistral response
    user_prompt = build_prompt(domain, test_emails)
    response = ask_mistral(user_prompt).strip().lower()

    print(f"\n🤖 Mistral response:\n{response}\n")

    # ✨ Step 1: Parse score lines
    scored = []
    for line in response.splitlines():
        if ":" in line:
            try:
                email, score = line.split(":", 1)
                email = email.strip()
                score = float(score.strip())
                if email in test_emails:
                    scored.append((email, score))
            except ValueError:
                continue

    # ✨ Step 2: Sort and select highest score
    if scored:
        scored.sort(key=lambda x: x[1], reverse=True)
        top_email = scored[0][0]
        print(f"🎯 Mistral-approved: {top_email}")
        return [top_email]

    # ✨ Step 3: Fallback to domain-matching or first email
    print("⚠️ Mistral returned no usable result. Using fallback selection...")
    for email in test_emails:
        if domain in email:
            return [email]

    return [test_emails[0]]
