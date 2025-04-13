# filter/mistral_filter.py

import subprocess
from urllib.parse import urlparse
from utils.save import save_compact_recommendation_csv

# 🧠 Ask Mistral a question via subprocess using Ollama
def ask_mistral(prompt: str) -> str:
    """
    Sends a prompt to the local Mistral model using Ollama and returns the response.

    Args:
        prompt (str): The question or instruction to send to Mistral.

    Returns:
        str: The Mistral model's response (stripped and cleaned).
    """
    process = subprocess.Popen(
        ["ollama", "run", "mistral"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"  # Helps avoid encoding issues on Windows
    )

    stdout, stderr = process.communicate(prompt)

    if process.returncode != 0:
        print("⚠️ Mistral stderr:", stderr)
        return ""

    return stdout.strip()


# 🧠 Build the structured prompt to guide Mistral on email selection
def build_prompt(site: str, emails: list[str]) -> str:
    """
    Constructs the exact prompt format expected by Mistral for scoring emails.

    Args:
        site (str): The domain of the business website.
        emails (list[str]): List of scraped email addresses.

    Returns:
        str: A structured and rule-based prompt string.
    """
    return f"""
You are a website contact email validator.

Official website: {site}

Below is a list of email addresses scraped directly from pages on this site:
{chr(10).join(emails)}

Your task is to choose the single best email for a customer or client to reach this business regarding general inquiries, services, or sales.

Rules:
- ONLY choose from the emails in the list above. DO NOT make up or guess.
- Reply with just one email address only — no punctuation, no quotes, no commentary.
- Do not include duplicates or any email with subject/query parameters.
- Only return a real, valid email from the list.

Strictly follow these rules and do not deviate from them.

DO NOT create or suggest any new email addresses.

Score each email from 0.0 to 1.0 based on how likely it is to be the best contact email for this business.
- from 0.0 to 1.0, where 1.0 is the best email.
- 0.0 means the email is not valid or not a business contact email.
- 1.0 means the email is the best business contact email.
- Prefer emails that match the website domain.
- Prefer customer-facing emails like contact@, hello@, support@, sales@, or similar.
- Avoid emails meant for internal teams (e.g., employment@, media@, noreply@, admin@, info@).
- Avoid emails that look like placeholders or are malformed.

Strictly follow this format. DO NOT add any explanations or extra text.

Return output in **this exact format**:
- A list of all scored emails like this: email@example.com: 0.87

If there is no valid business contact email, return an empty string (nothing).
""".strip()


# 🌟 Use Mistral to evaluate and select the best email
def filter_emails_with_mistral(raw_emails: list[dict]) -> list[str]:
    """
    Given a list of email dicts with 'value' and 'source', selects the best business contact email
    using a LLM (Mistral via Ollama).

    Args:
        raw_emails (list[dict]): List of dicts like {"value": "email@domain.com", "source": "https://site"}

    Returns:
        list[str]: A list containing one recommended email, or an empty list if none are valid.
    """
    if not raw_emails:
        return []

    # 🧹 Normalize and extract just the email addresses
    email_list = [email['value'].strip().lower() for email in raw_emails]

    if len(email_list) == 1:
        print("⚠️ Only one email found. Using that one.")
        return [email_list[0]]

    # 🌐 Extract domain from the source URL
    site_url = raw_emails[0]['source']
    domain = urlparse(site_url).netloc.replace("www.", "")

    # 💌 Build prompt and query Mistral
    user_prompt = build_prompt(domain, email_list)
    response = ask_mistral(user_prompt).strip().lower()

    print(f"\n🤖 Mistral response:\n{response}\n")

    response_lines = response.splitlines()

    # 📊 Parse and score emails from response
    scored = []
    for line in response_lines[0:]:
        if ":" in line:
            try:
                email, score = line.split(":", 1)
                email = email.strip()
                score = float(score.strip())
                if email in email_list and score > 0.6:
                    scored.append((email, score))
            except ValueError:
                continue

    # 🎯 Choose the top-scored email or fallback
    recommended = ""

    if scored:
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        recommended = scored[0][0]
        print(f"🎯 Mistral-approved (from scores): {recommended}")
    else:
        print("⚠️ Mistral returned no usable result. Using fallback selection...")
        for email in email_list:
            if domain in email:
                recommended = email
                break
        if not recommended and len(email_list) == 1:
            recommended = email_list[0]

    # 💾 Save results to CSV
    save_compact_recommendation_csv(
        site=domain,
        recommended=recommended,
        email_scores=scored
    )

    return [recommended] if recommended else []
