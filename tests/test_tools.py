from unittest.mock import patch, MagicMock
from tools import get_unread_emails, draft_reply, get_labels, create_label, apply_label, save_preference, load_preferences
import json


@patch("tools.build_gmail_service")
def test_get_unread_emails_returns_list(mock_service):
    # Set up fake API response
    mock_gmail = MagicMock()
    mock_service.return_value = mock_gmail

    mock_gmail.users().messages().list().execute.return_value = {
        "messages": [{"id": "abc123"}]
    }
    mock_gmail.users().messages().get().execute.return_value = {
        "threadId": "thread1",
        "snippet": "Hey can we meet?",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Quick question"},
                {"name": "From", "value": "boss@work.com"},
            ]
        },
    }

    result = get_unread_emails()

    assert isinstance(result, list)
    assert result[0]["subject"] == "Quick question"
    assert result[0]["from"] == "boss@work.com"


@patch("tools.build_gmail_service")
def test_draft_reply_returns_draft_id(mock_service):
    mock_gmail = MagicMock()
    mock_service.return_value = mock_gmail

    mock_gmail.users().getProfile().execute.return_value = {
        "emailAddress": "me@gmail.com"
    }
    mock_gmail.users().drafts().create().execute.return_value = {
        "id": "draft_456"
    }

    result = draft_reply("thread1", "Sounds good, see you then.")

    assert result == "draft_456"


@patch("tools.build_gmail_service")
def test_get_labels_returns_list(mock_service):
    mock_gmail = MagicMock()
    mock_service.return_value = mock_gmail

    mock_gmail.users().labels().list().execute.return_value = {
        "labels": [
            {"id": "Label_1", "name": "Urgent"},
            {"id": "Label_2", "name": "Follow Up"},
        ]
    }

    result = get_labels()

    assert isinstance(result, list)
    assert result[0]["name"] == "Urgent"
    assert result[1]["id"] == "Label_2"


@patch("tools.build_gmail_service")
def test_create_label_returns_id(mock_service):
    mock_gmail = MagicMock()
    mock_service.return_value = mock_gmail

    mock_gmail.users().labels().create().execute.return_value = {
        "id": "Label_3",
        "name": "AI Policy"
    }

    result = create_label("AI Policy")

    assert result == "Label_3"


@patch("tools.build_gmail_service")
def test_apply_label_returns_message_id(mock_service):
    mock_gmail = MagicMock()
    mock_service.return_value = mock_gmail

    result = apply_label("msg_abc", "Label_1")

    assert result == "msg_abc"
    mock_gmail.users().messages().modify.assert_called_once_with(
        userId="me",
        id="msg_abc",
        body={"addLabelIds": ["Label_1"]}
    )


def test_save_preference_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.MEMORY_FILE", tmp_path / "memory.json")
    result = save_preference("urgent_senders", "ceo@company.com")
    assert result == "Saved: urgent_senders = ceo@company.com"
    assert (tmp_path / "memory.json").exists()


def test_save_preference_persists_value(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.MEMORY_FILE", tmp_path / "memory.json")
    save_preference("urgent_senders", "ceo@company.com")
    data = json.loads((tmp_path / "memory.json").read_text())
    assert data["urgent_senders"] == "ceo@company.com"


def test_load_preferences_returns_empty_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.MEMORY_FILE", tmp_path / "memory.json")
    result = load_preferences()
    assert result == {}


def test_load_preferences_returns_saved_data(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.MEMORY_FILE", tmp_path / "memory.json")
    save_preference("draft_style", "formal")
    result = load_preferences()
    assert result["draft_style"] == "formal"