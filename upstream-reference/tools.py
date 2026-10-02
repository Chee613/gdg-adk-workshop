import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path
import json


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

BASE_DIR = Path(__file__).parent
MEMORY_FILE = Path(__file__).parent / "memory.json"

def build_gmail_service():
    creds = None
    token_path = BASE_DIR / "token.json"
    creds_path = BASE_DIR / "credentials.json"
    
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def get_unread_emails() -> list:
    """Fetches the 10 most recent unread emails. Returns a list of subject and sender."""
    service = build_gmail_service()
    results = service.users().messages().list(
        userId="me",
        labelIds=["UNREAD"],
        maxResults=10,
    ).execute()

    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From"],
        ).execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        emails.append({
            "id": msg["id"],
            "thread_id": detail["threadId"],
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", "(unknown)"),
            "snippet": detail.get("snippet", ""),
        })
    return emails


def draft_reply(thread_id: str, reply_text: str) -> str:
    """Creates a draft reply to an email thread. Returns the draft ID."""
    service = build_gmail_service()
    profile = service.users().getProfile(userId="me").execute()
    my_email = profile["emailAddress"]

    message_body = f"To: {my_email}\r\nSubject: Re: (your reply)\r\n\r\n{reply_text}"
    encoded = base64.urlsafe_b64encode(message_body.encode()).decode()

    draft = service.users().drafts().create(
        userId="me",
        body={
            "message": {
                "threadId": thread_id,
                "raw": encoded,
            }
        },
    ).execute()
    return draft["id"]


def get_labels() -> list:
    """Returns all existing Gmail labels for the user's inbox."""
    service = build_gmail_service()
    results = service.users().labels().list(userId="me").execute()
    return [{"id": l["id"], "name": l["name"]} for l in results.get("labels", [])]


def create_label(name: str) -> str:
    """Creates a new Gmail label with the given name. Returns the label ID."""
    service = build_gmail_service()
    label = service.users().labels().create(
        userId="me",
        body={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
    ).execute()
    return label["id"]


def apply_label(message_id: str, label_id: str) -> str:
    """Applies a label to an email by message ID. Returns the message ID."""
    service = build_gmail_service()
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]}
    ).execute()
    return message_id


def save_preference(key: str, value: str) -> str:
    """Saves a user preference for future sessions so the agent remembers it next time."""
    memory = json.loads(MEMORY_FILE.read_text()) if MEMORY_FILE.exists() else {}
    memory[key] = value
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))
    return f"Saved: {key} = {value}"


def load_preferences() -> dict:
    """Loads all saved user preferences from previous sessions."""
    if not MEMORY_FILE.exists():
        return {}
    return json.loads(MEMORY_FILE.read_text())