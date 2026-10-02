from dotenv import load_dotenv
from pathlib import Path
from google.adk.agents import LlmAgent
from .tools import get_unread_emails, draft_reply, get_labels, create_label, apply_label, save_preference, load_preferences

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

root_agent = LlmAgent(
    model="gemini-2.5-flash",

    name="email_assistant",

    instruction="""
        You are a sharp, efficient email assistant who values the user's time.
        You have access to their Gmail. Be proactive — surface what matters,
        ignore what doesn't, and always draft before sending anything.
    """,

    tools=[
        get_unread_emails,
        draft_reply,
        get_labels,
        create_label,
        apply_label,
        save_preference,
        load_preferences,
    ],
)


