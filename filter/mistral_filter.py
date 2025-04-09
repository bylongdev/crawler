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

Your task is to choose the single best email for a customer or client to reach this business regarding general inquiries, services, or sales.

Rules:
- ONLY choose from the emails in the list above. DO NOT make up or guess.
- Reply with just one email address only — no punctuation, no quotes, no commentary.
- Prefer emails that match the website domain.
- Prefer customer-facing emails like contact@, hello@, support@, sales@, or similar.
- Avoid emails meant for internal teams (e.g., employment@, media@, noreply@, admin@, info@).
- Avoid emails that look like placeholders or are malformed.
- Only return a real, valid email from the list.

Return output in this exact format:
- First line: the single best contact email (for customers/sales)
- Then, on the next lines: a list of all scored emails like this:
email@example.com: 0.87

Strictly follow the format above. Do not add any explanations or extra text.
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
