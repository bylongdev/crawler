# filter/mistral_filter.py

import subprocess
from urllib.parse import urlparse
from utils.save import save_compact_recommendation_csv

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

Strictly follow these rules and do not deviate from them.

Return only the email address on a single line with no explanation or further text.

Additionally, include a score (between 0.0 and 1.0) for each email in this format:
email@example.com: 0.85
The scores should reflect how suitable each email is as a business contact.
""".strip()


def filter_emails_with_mistral(raw_emails: list[dict]) -> list[str]:
    if not raw_emails:
        return []

    email_list = [email['value'].strip().lower() for email in raw_emails]

    site_url = raw_emails[0]['source']
    domain = urlparse(site_url).netloc.replace("www.", "")

    # 🧠 Build prompt and ask Mistral
    user_prompt = build_prompt(domain, email_list)
    response = ask_mistral(user_prompt).strip().lower()

    print(f"\n🤖 Mistral response:\n{response}\n")

    # 🧠 Parse scored response
    scored = []
    for line in response.splitlines():
        if ":" in line:
            try:
                email, score = line.split(":", 1)
                email = email.strip()
                score = float(score.strip())
                if email in email_list:
                    scored.append((email, score))
            except ValueError:
                continue

    recommended = ""

    # 🎯 Pick top-scoring email
    if scored:
        scored.sort(key=lambda x: x[1], reverse=True)
        recommended = scored[0][0]
        print(f"🎯 Mistral-approved: {recommended}")
    else:
        print("⚠️ Mistral returned no usable result. Using fallback selection...")
        for email in email_list:
            if domain in email:
                recommended = email
                break
        if not recommended and len(email_list) == 1:
            recommended = email_list[0]

    # 💾 Save compact result
    save_compact_recommendation_csv(
        site=domain,
        recommended=recommended,
        email_scores=scored
    )

    return [recommended]
