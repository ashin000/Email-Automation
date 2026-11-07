"""Gmail API reader with read-only OAuth scope."""
import base64
from pathlib import Path
from email.utils import parseaddr
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.config import settings
from app.models import EmailMessage

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def _decode(data: str) -> str:
    try:
        return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="replace")
    except Exception:
        return ""

def _extract_body(payload: dict) -> str:
    data = payload.get("body", {}).get("data")
    mime = payload.get("mimeType", "")
    if data and (mime.startswith("text/plain") or not payload.get("parts")):
        return _decode(data)
    return "\n".join(filter(None, (_extract_body(p) for p in payload.get("parts", []) or []))).strip()

def _headers(payload: dict) -> dict:
    return {h.get("name","").lower(): h.get("value","") for h in payload.get("headers",[])}

def get_gmail_service():
    creds = None
    token_file: Path = settings.gmail_token_file
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not settings.gmail_credentials_file.exists():
            raise FileNotFoundError(f"Missing {settings.gmail_credentials_file}. Download OAuth Desktop credentials from Google Cloud.")
        flow = InstalledAppFlow.from_client_secrets_file(str(settings.gmail_credentials_file), SCOPES)
        creds = flow.run_local_server(port=0)
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def fetch_unread_emails(max_results: int | None = None) -> list[EmailMessage]:
    service = get_gmail_service()
    result = service.users().messages().list(userId="me", q=settings.gmail_query, maxResults=max_results or settings.gmail_max_results).execute()
    emails = []
    for item in result.get("messages", []):
        msg = service.users().messages().get(userId="me", id=item["id"], format="full").execute()
        payload = msg.get("payload", {})
        headers = _headers(payload)
        name, address = parseaddr(headers.get("from", ""))
        sender = f"{name} <{address}>" if name else (address or headers.get("from", "Unknown sender"))
        body = _extract_body(payload).strip() or msg.get("snippet", "")
        emails.append(EmailMessage(msg["id"], sender, headers.get("subject", "(No subject)"), body[:30000], headers.get("date", ""), msg.get("snippet", "")))
    return emails
