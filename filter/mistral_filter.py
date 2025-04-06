# filter/mistral_filter.py

import subprocess
import json

SYSTEM_PROMPT = (
    "You are a filtering assistant for a contact scraper bot.\n"
    "You will receive a list of email addresses scraped from a specific website.\n"
    "Your task is to select exactly ONE email address from the list that is most suitable for professional contact purposes.\n\n"
    "Rules:\n"
    "- ONLY choose from the provided list of emails. Do not generate or guess.\n"
    "- If there are multiple options, prefer the email address that matches the website’s domain.\n"
    "- If there is only one valid email in the list, return it—even if it is a personal email (e.g., Gmail, Outlook).\n"
    "- Exclude obviously fake, placeholder, or malformed emails (e.g., test@, hello@localhost, abc@123).\n"
    "- Your response must contain only the selected email address, with no additional text or explanation.\n"
    "Always return one valid email from the list, even if it is the only one available.\n"
)





def ask_mistral(prompt: str) -> str:
    """Send a prompt to Ollama (Mistral) and return the output"""
    result = subprocess.run(
        ["ollama", "run", "mistral:latest", prompt],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()

from urllib.parse import urlparse

def filter_emails_with_mistral(raw_emails: list[dict]) -> list[str]:
    if not raw_emails:
        return []

    email_list = [email['value'] for email in raw_emails]
    domain = urlparse(raw_emails[0]['source']).netloc.replace("www.", "")

    user_prompt = SYSTEM_PROMPT + f"\nWebsite domain: {domain}\n\nEmails:\n"
    user_prompt += "\n".join(email_list)

    response = ask_mistral(user_prompt).strip().lower()

    # 🧠 Step 1: Trust Mistral if she picks one of the valid emails
    if response in email_list:
        return [response]

    # 🛡️ Step 2: If she gives no answer or weird one → Fallback logic
    print("⚠️ Mistral returned nothing valid. Using fallback selection...")

    # Try to find email that matches domain
    for email in email_list:
        if domain in email:
            return [email]

    # Else just return the first one as last resort
    return [email_list[0]]


