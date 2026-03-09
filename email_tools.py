"""Email tools – callable functions exposed to the LLM via AISuite."""

import requests

BASE_URL = "http://127.0.0.1:8765"


def list_all_emails() -> list:
    """Fetch all emails, newest first."""
    r = requests.get(f"{BASE_URL}/emails")
    return r.json()


def list_unread_emails() -> list:
    """Retrieve only unread emails."""
    r = requests.get(f"{BASE_URL}/emails/unread")
    return r.json()


def search_emails(query: str) -> list:
    """Search emails by keyword in subject, body, or sender.

    Args:
        query: The keyword to search for.
    """
    r = requests.get(f"{BASE_URL}/emails/search", params={"q": query})
    return r.json()


def filter_emails(recipient: str = None, start_date: str = None, end_date: str = None) -> list:
    """Filter emails by recipient and/or date range.

    Args:
        recipient: Filter by recipient email address.
        start_date: Start date in ISO format (e.g. 2025-06-01).
        end_date: End date in ISO format (e.g. 2025-06-30).
    """
    params = {}
    if recipient:
        params["recipient"] = recipient
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    r = requests.get(f"{BASE_URL}/emails/filter", params=params)
    return r.json()


def get_email(email_id: int) -> dict:
    """Fetch a specific email by its ID.

    Args:
        email_id: The ID of the email to fetch.
    """
    r = requests.get(f"{BASE_URL}/emails/{email_id}")
    return r.json()


def mark_email_as_read(email_id: int) -> dict:
    """Mark an email as read.

    Args:
        email_id: The ID of the email to mark as read.
    """
    r = requests.patch(f"{BASE_URL}/emails/{email_id}/read")
    return r.json()


def mark_email_as_unread(email_id: int) -> dict:
    """Mark an email as unread.

    Args:
        email_id: The ID of the email to mark as unread.
    """
    r = requests.patch(f"{BASE_URL}/emails/{email_id}/unread")
    return r.json()


def send_email(recipient: str, subject: str, body: str) -> dict:
    """Send a new email.

    Args:
        recipient: The email address of the recipient.
        subject: The subject line of the email.
        body: The body text of the email.
    """
    r = requests.post(
        f"{BASE_URL}/send",
        json={"sender": "you@email.com", "recipient": recipient, "subject": subject, "body": body},
    )
    return r.json()


def delete_email(email_id: int) -> dict:
    """Delete an email by its ID.

    Args:
        email_id: The ID of the email to delete.
    """
    r = requests.delete(f"{BASE_URL}/emails/{email_id}")
    return r.json()


def search_unread_from_sender(sender_address: str) -> list:
    """Return unread emails from a given sender.

    Args:
        sender_address: The sender's email address (e.g. boss@email.com).
    """
    r = requests.get(f"{BASE_URL}/emails/unread", params={"sender": sender_address})
    return r.json()
