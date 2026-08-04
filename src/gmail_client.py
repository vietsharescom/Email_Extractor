"""Gmail API OAuth authentication and thin fetch wrapper.

Requires `credentials.json` (OAuth client secret, Desktop app type) in the
project root, downloaded from Google Cloud Console. First run opens a browser
for consent; `token.json` is then cached locally for reuse (both gitignored).
"""
import base64
import os
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"'{CREDENTIALS_FILE}' not found. Download OAuth client "
                    "credentials (Desktop app type) from Google Cloud Console "
                    "and place it in the project root."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _get_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return None


def list_message_ids(service, query="", max_results=500):
    """Return message ids matching a Gmail search query (e.g. 'newer_than:90d')."""
    ids = []
    page_token = None
    while True:
        resp = service.users().messages().list(
            userId="me", q=query, pageToken=page_token,
            maxResults=min(500, max_results - len(ids)),
        ).execute()
        ids.extend(m["id"] for m in resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token or len(ids) >= max_results:
            break
    return ids[:max_results]


def get_message_summary(service, msg_id):
    """Fetch metadata only (fast) — sender, subject, date, labelIds."""
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["From", "Subject", "Date"],
    ).execute()
    headers = msg["payload"]["headers"]
    from_raw = _get_header(headers, "From") or ""
    name, addr = parseaddr(from_raw)
    return {
        "id": msg_id,
        "thread_id": msg.get("threadId"),
        "sender_name": name,
        "sender_email": addr.lower(),
        "sender_domain": addr.split("@")[-1].lower() if "@" in addr else "",
        "subject": _get_header(headers, "Subject") or "",
        "date": _get_header(headers, "Date") or "",
        "label_ids": msg.get("labelIds", []),
        "snippet": msg.get("snippet", ""),
    }
