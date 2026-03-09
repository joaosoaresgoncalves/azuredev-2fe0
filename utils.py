"""Utility helpers – starts the email service and provides test wrappers."""

import json
import threading
import time
import requests
import uvicorn

BASE_URL = "http://127.0.0.1:8765"
_server_started = False


def _start_server():
    global _server_started
    if _server_started:
        return
    _server_started = True

    from email_server import app

    def _run():
        uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    # Wait until the server is responsive
    for _ in range(40):
        try:
            requests.get(f"{BASE_URL}/emails", timeout=1)
            return
        except Exception:
            time.sleep(0.25)


# Auto-start on import
_start_server()


# ── Pretty-print helper ────────────────────────────────────────
def print_html(content: str, title: str = ""):
    """Print formatted output (works in both notebook and terminal)."""
    separator = "=" * 50
    if title:
        print(f"\n{separator}\n  {title}\n{separator}")
    print(content)
    print(separator)


# ── Test helpers ────────────────────────────────────────────────
def test_send_email():
    r = requests.post(
        f"{BASE_URL}/send",
        json={
            "sender": "you@email.com",
            "recipient": "test@example.com",
            "subject": "Test Email",
            "body": "This is a test email.",
        },
    )
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_send_email")
    return data


def test_get_email(email_id: int):
    r = requests.get(f"{BASE_URL}/emails/{email_id}")
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_get_email")
    return data


def test_list_emails():
    r = requests.get(f"{BASE_URL}/emails")
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_list_emails")
    return data


def test_filter_emails(recipient: str = None, start_date: str = None, end_date: str = None):
    params = {}
    if recipient:
        params["recipient"] = recipient
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    r = requests.get(f"{BASE_URL}/emails/filter", params=params)
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_filter_emails")
    return data


def test_search_emails(query: str):
    r = requests.get(f"{BASE_URL}/emails/search", params={"q": query})
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_search_emails")
    return data


def test_unread_emails():
    r = requests.get(f"{BASE_URL}/emails/unread")
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_unread_emails")
    return data


def test_mark_read(email_id: int):
    r = requests.patch(f"{BASE_URL}/emails/{email_id}/read")
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_mark_read")
    return data


def test_mark_unread(email_id: int):
    r = requests.patch(f"{BASE_URL}/emails/{email_id}/unread")
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_mark_unread")
    return data


def test_delete_email(email_id: int):
    r = requests.delete(f"{BASE_URL}/emails/{email_id}")
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="test_delete_email")
    return data


def reset_database():
    r = requests.get(f"{BASE_URL}/reset_database")
    data = r.json()
    print_html(content=json.dumps(data, indent=2), title="reset_database")
    return data
