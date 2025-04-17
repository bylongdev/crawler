# Converted version of mistral_filter.py using a class-based structure

import subprocess
from urllib.parse import urlparse
from utils.save import save_compact_recommendation_csv
import re

class MistralEmailFilter:
    """
    Uses the local Mistral LLM model via Ollama to intelligently score and recommend the best email address from a list.
    """
    @staticmethod
    def ask_mistral(prompt: str) -> str:
        """Send a structured prompt to Mistral and retrieve the response."""
        process = subprocess.Popen(
            ["ollama", "run", "mistral"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        stdout, stderr = process.communicate(prompt)
        if process.returncode != 0:
            print("⚠️ Mistral stderr:", stderr)
            return ""
        return stdout.strip()

    @staticmethod
    def build_prompt(site: str, emails: list[str]) -> str:
        """Build the exact scoring prompt for Mistral."""
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
    
    @staticmethod
    def clean_email(e: str) -> str | None:
        e = e.strip().lower()
        if not e or "@" not in e:
            return None
        if any(bad in e for bad in ["noreply", "no-reply", "do-not-reply", ".jpg", ".png", ".gif", "utm_", "+"]):
            return None
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", e):
            return None
        return e

    

    def filter(self, raw_emails: list[dict]) -> list[str]:
        """
        Main filtering method: accepts a list of emails + source, returns the most suitable one.
        """
        if not raw_emails:
            return []

        seen = set()
        email_list = []

        for email in raw_emails:
            cleaned = self.clean_email(email['value'])
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                email_list.append(cleaned)

        if len(email_list) == 1:
            print("⚠️ Only one email found. Using that one.")
            return [email_list[0]]

        site_url = raw_emails[0]['source']
        domain = urlparse(site_url).netloc.replace("www.", "")

        prompt = self.build_prompt(domain, email_list)
        response = self.ask_mistral(prompt).strip().lower()
        print(f"🤖 Mistral response:\n{response}\n")

        scored = []
        for line in response.splitlines():
            if ":" in line:
                try:
                    email, score = line.split(":", 1)
                    email = email.strip()
                    score = float(score.strip())
                    if email in email_list and score > 0.6:
                        scored.append((email, score))
                except ValueError:
                    continue

        recommended = ""
        if scored:
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

        save_compact_recommendation_csv(
            site=domain,
            recommended=recommended,
            email_scores=scored
        )

        return recommended