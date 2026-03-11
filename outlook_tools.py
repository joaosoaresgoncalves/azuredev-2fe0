"""Outlook tools – callable functions exposed to the LLM via AISuite.

Uses a Microsoft Graph Explorer access token (from .env)
to interact with a real Outlook mailbox.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def _get_token() -> str:
    """Return the Graph Explorer access token from the environment."""
    token = os.getenv("GRAPH_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Missing GRAPH_ACCESS_TOKEN in .env. "
            "Copy it from https://developer.microsoft.com/graph/graph-explorer → Access token tab."
        )
    return token


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_get_token()}",
        "Content-Type": "application/json",
    }


# ── Email tools ─────────────────────────────────────────────────

def list_all_emails(top: int = 25) -> list:
    """Fetch the most recent emails from the Outlook inbox, newest first.

    Args:
        top: Maximum number of emails to return (default 25).
    """
    r = requests.get(
        f"{GRAPH_BASE}/me/messages",
        headers=_headers(),
        params={
            "$top": top,
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,toRecipients,bodyPreview,receivedDateTime,isRead",
        },
    )
    r.raise_for_status()
    return [_normalize(m) for m in r.json().get("value", [])]


def list_unread_emails(top: int = 25) -> list:
    """Retrieve only unread emails from the Outlook inbox.

    Args:
        top: Maximum number of emails to return (default 25).
    """
    r = requests.get(
        f"{GRAPH_BASE}/me/messages",
        headers=_headers(),
        params={
            "$top": top,
            "$filter": "isRead eq false",
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,toRecipients,bodyPreview,receivedDateTime,isRead",
        },
    )
    r.raise_for_status()
    return [_normalize(m) for m in r.json().get("value", [])]


def search_emails(query: str, top: int = 25) -> list:
    """Search emails by keyword in subject, body, or sender.

    Args:
        query: The keyword to search for.
        top: Maximum number of results (default 25).
    """
    r = requests.get(
        f"{GRAPH_BASE}/me/messages",
        headers=_headers(),
        params={
            "$search": f'"{query}"',
            "$top": top,
            "$select": "id,subject,from,toRecipients,bodyPreview,receivedDateTime,isRead",
        },
    )
    r.raise_for_status()
    return [_normalize(m) for m in r.json().get("value", [])]


def get_email(email_id: str) -> dict:
    """Fetch a specific email by its ID.

    Args:
        email_id: The Graph API message ID.
    """
    r = requests.get(
        f"{GRAPH_BASE}/me/messages/{email_id}",
        headers=_headers(),
        params={
            "$select": "id,subject,from,toRecipients,body,receivedDateTime,isRead",
        },
    )
    r.raise_for_status()
    data = r.json()
    return {
        "id": data["id"],
        "sender": data.get("from", {}).get("emailAddress", {}).get("address", ""),
        "recipient": ", ".join(
            r["emailAddress"]["address"] for r in data.get("toRecipients", [])
        ),
        "subject": data.get("subject", ""),
        "body": data.get("body", {}).get("content", ""),
        "timestamp": data.get("receivedDateTime", ""),
        "read": data.get("isRead", False),
    }


def mark_email_as_read(email_id: str) -> dict:
    """Mark an email as read.

    Args:
        email_id: The Graph API message ID.
    """
    r = requests.patch(
        f"{GRAPH_BASE}/me/messages/{email_id}",
        headers=_headers(),
        json={"isRead": True},
    )
    r.raise_for_status()
    return {"id": email_id, "read": True, "status": "marked as read"}


def mark_email_as_unread(email_id: str) -> dict:
    """Mark an email as unread.

    Args:
        email_id: The Graph API message ID.
    """
    r = requests.patch(
        f"{GRAPH_BASE}/me/messages/{email_id}",
        headers=_headers(),
        json={"isRead": False},
    )
    r.raise_for_status()
    return {"id": email_id, "read": False, "status": "marked as unread"}


def send_email(recipient: str, subject: str, body: str) -> dict:
    """Send a new email via Outlook.

    Args:
        recipient: The email address of the recipient.
        subject: The subject line of the email.
        body: The body text of the email.
    """
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [
                {"emailAddress": {"address": recipient}}
            ],
        }
    }
    r = requests.post(
        f"{GRAPH_BASE}/me/sendMail",
        headers=_headers(),
        json=payload,
    )
    r.raise_for_status()
    return {
        "status": "sent",
        "recipient": recipient,
        "subject": subject,
    }


def delete_email(email_id: str) -> dict:
    """Delete an email by its ID.

    Args:
        email_id: The Graph API message ID.
    """
    r = requests.delete(
        f"{GRAPH_BASE}/me/messages/{email_id}",
        headers=_headers(),
    )
    r.raise_for_status()
    return {"id": email_id, "status": "deleted"}


def search_unread_from_sender(sender_address: str) -> list:
    """Return unread emails from a given sender.

    Args:
        sender_address: The sender's email address (e.g. boss@company.com).
    """
    r = requests.get(
        f"{GRAPH_BASE}/me/messages",
        headers=_headers(),
        params={
            "$filter": f"isRead eq false and from/emailAddress/address eq '{sender_address}'",
            "$orderby": "receivedDateTime desc",
            "$select": "id,subject,from,toRecipients,bodyPreview,receivedDateTime,isRead",
        },
    )
    r.raise_for_status()
    return [_normalize(m) for m in r.json().get("value", [])]


# ── Helpers ─────────────────────────────────────────────────────

def _normalize(msg: dict) -> dict:
    """Convert a Graph API message to the same flat dict format used by the simulated tools."""
    return {
        "id": msg["id"],
        "sender": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
        "recipient": ", ".join(
            r["emailAddress"]["address"] for r in msg.get("toRecipients", [])
        ),
        "subject": msg.get("subject", ""),
        "body": msg.get("bodyPreview", ""),
        "timestamp": msg.get("receivedDateTime", ""),
        "read": msg.get("isRead", False),
    }
