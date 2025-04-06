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

Your task is to choose the most likely official business contact email from this list.

Rules:
- ONLY choose from the emails in the list above. DO NOT make up or guess.
- Reply with just one email address only — no punctuation, no quotes, no commentary.
- Prefer emails that match the website domain.
- Do not include duplicates or any email with subject/query parameters.
- Only return a real, valid email from the list.
- If there is no valid business contact email, return an empty string (nothing).

Return only the email address on a single line.
""".strip()

def filter_emails_with_mistral(raw_emails: list[dict]) -> list[str]:
    if not raw_emails:
        return []

    email_list = [email['value'].strip().lower() for email in raw_emails]
    site_url = raw_emails[0]['source']
    domain = urlparse(site_url).netloc.replace("www.", "")

    user_prompt = build_prompt(domain, email_list)
    response = ask_mistral(user_prompt).strip().lower()

    print(f"🤖 Mistral response: {response}")

    # Trust only exact match from provided list
    if response in email_list:
        return [response]

    print("⚠️ Mistral returned nothing valid. Using fallback selection...")

    # Try domain-matching fallback
    for email in email_list:
        if domain in email:
            return [email]

    return [email_list[0]]
