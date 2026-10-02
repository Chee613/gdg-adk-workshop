# Inbox Buddy — your first Google ADK app

A beginner workshop with a small inbox assistant and an editable GDG slide deck. Read emails, ask what needs attention, and review a reply before saving it.

Forked from [scspai/adk-email-agent](https://github.com/scspai/adk-email-agent). The original teaching files are preserved in [upstream-reference](upstream-reference/). This version adds a browser interface, a fictional inbox and a separate approval step.

## Start here

Use **Python 3.11 or newer**. Checked with Python 3.12 and ADK 2.11.0.

Windows PowerShell:

```powershell
git clone https://github.com/Chee613/gdg-adk-workshop.git
cd gdg-adk-workshop
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

macOS / Linux:

```bash
git clone https://github.com/Chee613/gdg-adk-workshop.git
cd gdg-adk-workshop
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Open **http://127.0.0.1:8001/** for the demo and **http://127.0.0.1:8001/slides.html** for the slides. Stop the server with Ctrl+C. If port 8001 is occupied, stop the other copy before running this one.

No API key or Gmail account is needed for the first walkthrough. Its responses are **scripted**: it rehearses the interface, not live AI. Internet access is needed to install packages. Fonts have a local fallback.

## Try the demo

1. Click **Summarize my inbox**. Check the six fictional emails and expand the tool steps.
2. Click **What needs my attention?**. Review the proposed **Follow up** label. Confirm it or decline it.
3. Click **Draft a reply to the interview email**. Check the recipient and your availability. Edit a sentence, then click **Confirm & save draft**.
4. Open **Saved drafts** to see the approved text. Nothing is sent.
5. Click **Remember: keep replies concise**. Expand **What Buddy remembers**.
6. Choose **New private session** to start fresh. The new session has no saved drafts or preferences.

The scripted draft always uses the sample interview invitation. Free-form requests need a real model. Sample dates are fictional weekday examples, not reminders tied to today's date.

## Turn on real AI

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/). Copy `.env.example` to `.env` and edit it locally:

```dotenv
GOOGLE_API_KEY=your_key_here
ADK_MODEL=gemini-flash-latest
GMAIL_ENABLED=false
```

Restart the server. The mode indicator will say **Sample inbox · real ADK + Gemini**. ADK now runs the agent loop and Gemini chooses tools. The inbox is still fictional. Try a follow-up such as “Make that reply shorter.” Check the results; AI output can vary.

The model alias is configurable. Choose a model available to your API key if the default is unavailable. Costs, quotas and model access depend on your account. The browser never receives the key.

## Optional: use your Gmail

Do this before the workshop, or as an extra exercise. It is not needed for the main lesson.

1. Create a Google Cloud project and enable the Gmail API.
2. Set up the OAuth consent screen. Add your account as a test user when using an external app in testing.
3. Create an OAuth client of type **Desktop app**. Download its JSON as `credentials.json` in this folder.
4. Run `.\.venv\Scripts\python.exe connect_gmail.py` (macOS/Linux: `.venv/bin/python connect_gmail.py`). Complete Google's sign-in and consent yourself.
5. Keep the Gemini key in `.env`, set `GMAIL_ENABLED=true`, and restart the server.
6. Confirm the mode says **Your Gmail · real ADK + Gemini** before asking it to read emails.

See [Google's Gmail Python quickstart](https://developers.google.com/workspace/gmail/api/quickstart/python) for Cloud and OAuth setup.

Gmail mode reads up to ten messages per search. It extracts message text; attachments are not read. Retrieved email text and your chat are sent to Gemini when the agent runs. Only connect a mailbox you intend to use this way.

OAuth uses `gmail.modify`, a broad Gmail permission. This app exposes no sending, deleting or archiving tool, and blocks Trash/Spam label changes. Drafts and labels are written only after the relevant confirmation click. If a save times out, check Gmail before retrying: a remote write may have succeeded before the response was lost.

`credentials.json`, `token.json`, `.env` and old memory files are ignored by Git. Keep them private. To disconnect, set `GMAIL_ENABLED=false`, restart, and revoke the app's access in your Google account if desired.

## How it works

```text
Your browser → local Python server → ADK Runner → Gemini
                                           ↕
                                   Python inbox tools

Agent proposes → you review/edit → confirmation endpoint saves
```

Google ADK is an open-source toolkit for building agent apps. Gemini is the AI model. A tool is a Python function the model can ask the app to run. ADK runs the conversation: model request, tool call, tool result, then another model step or an answer.

This app uses one `LlmAgent`, six tools and one ADK session per browser session. `approve()` is absent from the agent's tools. Approval happens through the browser. Email contents are untrusted data; instructions inside an email are not user permission. A suspicious sample message helps teach this distinction.

| File | What to look at |
| --- | --- |
| [inbox_agent/agent.py](inbox_agent/agent.py) | Agent, model, instructions and tools |
| [inbox_agent/tools.py](inbox_agent/tools.py) | Sample inbox, proposals and preferences |
| [inbox_agent/gmail.py](inbox_agent/gmail.py) | Gmail reads, drafts and approved labels |
| [app.py](app.py) | ADK Runner, sessions and confirmation endpoints |
| [static/](static/) | HTML, CSS and JavaScript interface and slides |
| [connect_gmail.py](connect_gmail.py) | Explicit desktop OAuth setup |

Chats, sample drafts, proposals and preferences live in server memory. A new browser session gives a fresh view; restarting clears all in-memory sessions. Real Gmail drafts and labels already saved remain in Gmail. At most 32 sessions are kept. The server listens only on `127.0.0.1`. Shared hosting would need account authentication, durable storage and a deployment review.

## Slides and teaching notes

Open [static/slides.html](static/slides.html) in a browser, or use the running server. **← / →** move, **Home / End** jump, and **N** opens presenter notes.

The deck explains agents and ADK from zero, compares ADK with Codex and Claude Code, shows other projects to explore, and finishes with the inbox demo.

- [Presenter guide](docs/PRESENTER.md)
- [Source links](docs/SOURCES.md)
- [3D artwork prompts and provenance](docs/ARTWORK.md)

ADK is a toolkit for a custom app. Codex and Claude Code are ready agents for coding and other supported work; both also have SDKs and integrations. ADK helps us write our own tools, steps and interface. It is not automatically smarter or cheaper. Coding agents can help build an ADK application.

## More projects to explore

[Awesome ADK Agents](https://github.com/Sri-Krishna-V/awesome-adk-agents) is a collection of links and examples. Read each project's setup before trying it.

- [Travel planner](https://github.com/AashiDutt/Google-Agent-Development-Kit-Demo): ideas for flights, stays and activities.
- [Voice calendar assistant](https://github.com/bhancockio/adk-voice-agent): ask about your schedule by voice.
- [Excel chart agent](https://github.com/jenyss/google-adk-data-visualization-agent): ask questions about spreadsheet data. Its author marks this version as older; the [voice-to-chart version](https://github.com/jenyss/google-adk-voice-to-visualization-agent) is the suggested follow-up.

These are learning references, not integrations included in Inbox Buddy. Their dependencies, keys and permissions vary.

## Offline check

```powershell
.\.venv\Scripts\python.exe -m unittest test_workshop -v
```

Checks session isolation, review before saving, edited text, safe reply headers, fresh Gmail results, destructive-label rejection and a real ADK Runner round trip using an offline model double. It forces sample settings and never calls Gemini or Gmail. Live provider/OAuth behaviour still needs your credentials and an integration check.

## Credits and license

Original project: [SCSP's ADK email agent](https://github.com/scspai/adk-email-agent). Apache 2.0 license retained in [LICENSE](LICENSE). Original source and teaching PDF remain in `upstream-reference/` for comparison.

Changes include a fictional inbox, custom interface, review controls, session-only preferences, and reply recipient/thread handling. Generated 3D art is illustrative, not an app screenshot or official Google artwork.

Built with [Google ADK](https://adk.dev/), Gemini, FastAPI and plain browser code.
