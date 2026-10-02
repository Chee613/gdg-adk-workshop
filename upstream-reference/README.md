# Email Agent

A working AI agent that reads your Gmail, organizes important emails with labels, drafts replies, and remembers your preferences across sessions. Built with [Google's Agent Development Kit (ADK)](https://adk.dev) and Gemini 2.5 Flash.

This project was built as part of a lunch and learn at [SCSP](https://www.scsp.ai) to demonstrate how to build a real, tested AI agent from scratch.

---

## What It Does

The agent connects to your Gmail and can:

- Fetch and summarize your most recent unread emails
- Check existing Gmail labels and create new ones when needed
- Apply labels to emails it decides are important
- Draft replies for your review (never sends automatically)
- Save preferences across sessions so it learns how you like your inbox managed

---

## Project Structure

```
email_agent/
├── __init__.py          # makes it a Python package
├── .env                 # your Google API key (not committed)
├── agent.py             # the agent definition
├── tools.py             # Gmail tools + memory tools
├── credentials.json     # OAuth credentials from Google Cloud (not committed)
├── memory.json          # saved agent preferences (auto-created on first run)
├── token.json           # Gmail auth token (auto-created on first run)
└── tests/
    ├── conftest.py
    ├── test_tools.py
    └── test_agent.py
```

---

## Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com) account for your Gemini API key
- A [Google Cloud](https://console.cloud.google.com) project with the Gmail API enabled

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/scsp/email-agent.git
cd email-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install google-adk python-dotenv google-auth-oauthlib google-api-python-client pytest
```

### 4. Set up your Gemini API key

Go to [aistudio.google.com](https://aistudio.google.com), create an API key, then create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_key_here
```

### 5. Set up Gmail API access

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a new project
2. Navigate to APIs & Services > Library, search for "Gmail API" and enable it
3. Navigate to APIs & Services > Credentials > Create Credentials > OAuth Client ID
4. Choose Desktop App, give it a name (e.g. Email Agent), and download the JSON
5. Rename the downloaded file to `credentials.json` and place it in the project root
6. Add yourself as a test user under APIs & Services > OAuth Consent Screen > Test Users

The first time you run the agent it will open a browser window asking you to authorize Gmail access. After that it saves a `token.json` file locally and never asks again.

---

## Running the Agent

From inside the `email_agent` folder with your venv activated:

```bash
# Terminal interface
adk run email_agent

# Or browser UI at http://localhost:8000
cd ~/Desktop
adk web email_agent
```

Try prompting it with:

```
Check my emails and flag anything important.
```

---

## Running Tests

```bash
pytest tests/
```

All tests mock the Gmail API so no real network calls are made.

---

## How It Works

The agent is built on Google ADK's `LlmAgent` class. It has access to 7 tools:

| Tool | What it does |
|---|---|
| `get_unread_emails()` | Fetches the 10 most recent unread emails |
| `draft_reply()` | Creates a draft reply in Gmail |
| `get_labels()` | Returns all existing Gmail labels |
| `create_label()` | Creates a new Gmail label |
| `apply_label()` | Applies a label to an email |
| `save_preference()` | Saves a user preference to `memory.json` |
| `load_preferences()` | Loads saved preferences at the start of each session |

The agent decides which tools to call and in what order based on the user's request. No hardcoded logic — Gemini reasons through it at runtime.

Memory is stored as a plain JSON file on your local machine. You can open, edit, or delete it at any time.

---

## Further Reading

- [Google ADK Documentation](https://adk.dev)
- [Google ADK GitHub](https://github.com/google/adk-python)
- [Google ADK Sample Agents](https://github.com/google/adk-samples)

---

## License

Apache 2.0. See [LICENSE](./LICENSE) for details.
