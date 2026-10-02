"""Gmail integration. Only the review endpoint calls the write functions."""
import base64
from email.message import EmailMessage
from email.utils import parseaddr
from html.parser import HTMLParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def header(value: str) -> str:
    if any(ord(c) < 32 for c in value) or len(value) > 1000:
        raise ValueError("Invalid email header.")
    return value


def reply_address(original: dict) -> str:
    source = header(original.get("reply_to") or original["sender"])
    address = parseaddr(source)[1]
    if not address or "@" not in address:
        raise ValueError("This email has no usable reply address.")
    return address


def create_reply_message(original: dict, body: str) -> dict:
    """Keep the actual recipient, subject and thread; never address a reply to ourselves."""
    msg = EmailMessage()
    msg["To"] = reply_address(original)
    subject = header(original["subject"])
    msg["Subject"] = subject if subject.lower().startswith("re:") else "Re: " + subject
    message_id = header(original.get("message_id", ""))
    references = header(original.get("references", ""))
    if message_id:
        msg["In-Reply-To"] = message_id
        msg["References"] = (references + " " + message_id).strip()
    msg.set_content(body)
    return {"threadId": original.get("thread_id", original["id"]),
            "raw": base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")}


def build_gmail_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    token = BASE_DIR / "token.json"
    if not token.exists():
        raise ValueError("Gmail is not connected. Run python connect_gmail.py first.")
    creds = Credentials.from_authorized_user_file(str(token), SCOPES)
    if not creds.valid:
        if not creds.refresh_token:
            raise ValueError("Reconnect Gmail with python connect_gmail.py.")
        creds.refresh(Request())
        token.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        if tag in ("p", "br", "div", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def body_text(payload: dict) -> str:
    """Read text MIME parts only. Attachments never enter the agent context."""
    plain, html = [], []

    def visit(part):
        data = part.get("body", {}).get("data")
        if data and not part.get("filename"):
            text = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="replace")
            if part.get("mimeType") == "text/plain":
                plain.append(text)
            elif part.get("mimeType") == "text/html":
                html.append(text)
        for child in part.get("parts", []):
            visit(child)

    visit(payload)
    if plain:
        return "\n".join(plain)[:6000]
    parser = PlainText()
    parser.feed("\n".join(html))
    return "".join(parser.parts)[:6000]


def fetch_emails(query: str = "is:unread") -> list:
    service = build_gmail_service()
    found = service.users().messages().list(userId="me", q=query, maxResults=10).execute()
    labels = {x["id"]: x["name"] for x in service.users().labels().list(userId="me").execute().get("labels", [])}
    emails = []
    for item in found.get("messages", []):
        detail = service.users().messages().get(userId="me", id=item["id"], format="full").execute()
        fields = {x["name"].lower(): x["value"] for x in detail["payload"].get("headers", [])}
        emails.append({"id": detail["id"], "thread_id": detail["threadId"],
                       "sender": fields.get("from", "Unknown sender"),
                       "reply_to": fields.get("reply-to", ""),
                       "subject": fields.get("subject", "(No subject)"),
                       "body": body_text(detail["payload"]) or detail.get("snippet", ""),
                       "message_id": fields.get("message-id", ""), "references": fields.get("references", ""),
                       "labels": [labels.get(x, x) for x in detail.get("labelIds", [])],
                       "unread": "UNREAD" in detail.get("labelIds", [])})
    return emails


def save_draft(original: dict, body: str) -> str:
    result = build_gmail_service().users().drafts().create(
        userId="me", body={"message": create_reply_message(original, body)}).execute()
    return result["id"]


def safe_label(name: str) -> str:
    if name.upper() in ("TRASH", "SPAM"):
        raise ValueError("This workshop cannot move email to Trash or Spam. Choose a review label instead.")
    return name


def apply_label(message_id: str, name: str):
    name = safe_label(name)
    service = build_gmail_service()
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    label_id = next((x["id"] for x in labels if x["name"] == name), None)
    if not label_id:
        label_id = service.users().labels().create(userId="me", body={"name": name}).execute()["id"]
    service.users().messages().modify(userId="me", id=message_id, body={"addLabelIds": [label_id]}).execute()
