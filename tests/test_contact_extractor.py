# tests/test_contact_extractor.py

from extractor.contact_extractor import extract_contacts_from_html

def test_extract_single_email():
    html = "<html><body>Contact us at hello@catmail.com</body></html>"
    contacts = extract_contacts_from_html(html, source_url="https://example.com")

    assert len(contacts) == 1
    assert contacts[0]["type"] == "email"
    assert contacts[0]["value"] == "hello@catmail.com"

def test_extract_duplicate_emails():
    html = """
    <html><body>
        Reach us at hello@catmail.com or email hello@catmail.com again!
    </body></html>
    """
    contacts = extract_contacts_from_html(html, source_url="https://example.com")
    assert len(contacts) == 1, "Should deduplicate emails"

def test_extract_email_limit():
    html = "<html><body>" + " ".join(
        [f"user{i}@catmail.com" for i in range(20)]
    ) + "</body></html>"

    contacts = extract_contacts_from_html(html, source_url="https://example.com")
    assert len(contacts) == 10, "Should limit to 10 emails max"
