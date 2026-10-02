"""Small offline regression check: python -m unittest test_workshop -v."""
import base64
import os
import unittest
from email import policy
from email.parser import BytesParser
from unittest.mock import patch

from inbox_agent.tools import InboxSession
from inbox_agent.gmail import create_reply_message


class WorkshopCheck(unittest.TestCase):
    def test_http_review_and_foreign_origin(self):
        from fastapi.testclient import TestClient
        from app import app
        settings = patch.dict(os.environ, {"GOOGLE_API_KEY": "", "GMAIL_ENABLED": "false"})
        settings.start()
        self.addCleanup(settings.stop)
        client = TestClient(app)
        response = client.post("/api/session", json={})
        self.assertEqual(response.status_code, 200)
        session = response.json()
        auth = {"X-Session-ID": session["session_id"]}
        self.assertEqual(client.get("/api/state").status_code, 401)
        self.assertEqual(client.post("/api/session", json={}, headers={"Origin": "https://evil.example"}).status_code, 403)
        result = client.post("/api/chat", json={"message": "Draft a reply to the interview email"}, headers=auth).json()
        self.assertEqual(len(result["drafts"]), 0)
        action = result["pending"][0]
        other = client.post("/api/session", json={}).json()
        self.assertEqual(client.post(f"/api/actions/{action['id']}/approve", json={}, headers={"X-Session-ID": other["session_id"]}).status_code, 400)
        saved = client.post(f"/api/actions/{action['id']}/approve", json={"body": "Thanks. Please send the meeting link."}, headers=auth)
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json()["drafts"][0]["body"], "Thanks. Please send the meeting link.")
        self.assertEqual(client.post("/api/chat", json={"message": "x" * 4001}, headers=auth).status_code, 422)

    def test_review_boundary_and_session_isolation(self):
        inbox = InboxSession()
        other = InboxSession()
        action = inbox.propose_draft_reply("interview", "Thanks! I can attend.")
        self.assertEqual(inbox.drafts, [])
        self.assertEqual(other.pending, [])
        saved = inbox.approve(action["id"], "Thanks! Please confirm the venue.")
        self.assertEqual(saved["body"], "Thanks! Please confirm the venue.")
        self.assertEqual(saved["to"], "recruitment@example.com")
        self.assertEqual(inbox.pending, [])
        with self.assertRaises(ValueError):
            inbox.approve(action["id"])
        label = inbox.propose_label("interview", "Follow up")
        self.assertNotIn("Follow up", inbox.emails[0]["labels"])
        inbox.decline(label["id"])
        self.assertNotIn("Follow up", inbox.emails[0]["labels"])
        with self.assertRaises(ValueError):
            inbox.propose_draft_reply("not-loaded", "No")
        with self.assertRaises(ValueError):
            inbox.propose_label("interview", "Bad\nLabel")
        with self.assertRaises(ValueError):
            inbox.propose_label("interview", "Trash")
        with self.assertRaises(ValueError), patch("inbox_agent.gmail.build_gmail_service") as service:
            from inbox_agent.gmail import apply_label
            apply_label("interview", "SPAM")
        service.assert_not_called()
        live = InboxSession(live=True)
        with patch("inbox_agent.gmail.fetch_emails", side_effect=[[inbox.emails[0]], []]):
            self.assertEqual(len(live.get_unread_emails()), 1)
            self.assertEqual(live.get_unread_emails(), [])

    def test_real_adk_runner_with_offline_model(self):
        """Actual ADK loop + function tools; a fake model prevents network/API charges."""
        from fastapi.testclient import TestClient
        from app import app
        from google.adk.models.base_llm import BaseLlm
        from google.adk.models.llm_response import LlmResponse
        from google.genai import types
        from inbox_agent.agent import create_agent

        class OfflineModel(BaseLlm):
            async def generate_content_async(self, llm_request, stream=False):
                results = [part.function_response for content in llm_request.contents
                           for part in content.parts or [] if part.function_response]
                if not results:
                    part = types.Part(function_call=types.FunctionCall(name="search_emails", args={"query": "interview"}))
                elif len(results) == 1:
                    part = types.Part(function_call=types.FunctionCall(name="propose_draft_reply", args={"message_id": "interview", "reply_text": "Please send the meeting link."}))
                else:
                    part = types.Part(text="Your reply is ready for review.")
                yield LlmResponse(content=types.Content(role="model", parts=[part]))

        def offline_agent(inbox):
            agent = create_agent(inbox)
            agent.model = OfflineModel(model="offline-test")
            return agent

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "offline-test", "GMAIL_ENABLED": "false"}), patch("inbox_agent.agent.create_agent", side_effect=offline_agent):
            client = TestClient(app)
            session = client.post("/api/session", json={}).json()
            self.assertEqual(session["mode"], "sample-ai")
            response = client.post("/api/chat", json={"message": "Draft an interview reply"}, headers={"X-Session-ID": session["session_id"]})
            self.assertEqual(response.status_code, 200, response.text)
            data = response.json()
            self.assertEqual(data["reply"], "Your reply is ready for review.")
            self.assertEqual([item["tool"] for item in data["activity"]], ["search_emails", "propose_draft_reply"])
            self.assertEqual(data["drafts"], [])
            self.assertEqual(data["pending"][0]["to"], "recruitment@example.com")

    def test_reply_uses_sender_and_thread_headers(self):
        original = {"id": "a", "thread_id": "thread-a", "sender": "Recruiter <sender@example.com>",
                    "reply_to": "Replies <reply@example.com>", "subject": "Interview invitation",
                    "message_id": "<original@example.com>", "references": "<earlier@example.com>"}
        payload = create_reply_message(original, "Hello!\nThanks for the invitation.")
        msg = BytesParser(policy=policy.default).parsebytes(base64.urlsafe_b64decode(payload["raw"]))
        self.assertEqual(str(msg["To"]), "reply@example.com")
        self.assertEqual(str(msg["Subject"]), "Re: Interview invitation")
        self.assertEqual(str(msg["In-Reply-To"]), "<original@example.com>")
        self.assertEqual(str(msg["References"]), "<earlier@example.com> <original@example.com>")
        self.assertEqual(payload["threadId"], "thread-a")
        with self.assertRaises(ValueError):
            create_reply_message({**original, "subject": "Oops\r\nBcc: evil@example.com"}, "Hello")


if __name__ == "__main__":
    unittest.main()
