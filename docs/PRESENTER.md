# Google ADK beginner workshop

The deck has 19 slides and ends in the inbox demo. It assumes no agent knowledge. Participants can follow the explanation without Python experience. Reading and changing the code requires basic Python.

## Suggested timing

| Segment | Slides | Time |
|---|---|---:|
| Familiar task and agent basics | 1–3 | 5 minutes |
| ADK, tools and session context | 4–9 | 10 minutes |
| Honest comparison and architecture | 10–12 | 6 minutes |
| Demo scope, modes and approval | 13–15 | 5 minutes |
| Community projects | 16 | 3 minutes |
| Setup and live inbox exercise | 17–19 | 14 minutes |

Allow another 10–20 minutes if participants install Python and dependencies during the session. For a shorter session, prepare the app beforehand and talk through setup rather than waiting for installation.

For a two-hour workshop, use 20 minutes for slides 1–12, 60 minutes for the hands-on exercise below, 30 minutes to share changes and explore slide 16's projects, and 10 minutes for questions. Keep slides 18–19 for the closing demo.

## Two-hour hands-on exercise

| Time | Do this | Check the result |
|---|---|---|
| 0–15 min | Run the app and try the four walkthrough buttons. | Identify the fictional inbox, proposal and saved draft. |
| 15–30 min | Add a Gemini key locally, restart, and repeat in Sample + Gemini mode. | Expand tool activity. Explain which steps the model chose. |
| 30–45 min | Change one fictional message in `SAMPLE_EMAILS`, restart and ask for its summary. | Verify the summary against the message text. |
| 45–60 min | Change the agent's reply instructions. Ask for a draft, edit it and confirm. | Compare proposed and approved text. Run the offline check. |

Without model access, participants can try the interface, edit sample data and inspect `agent.py` with the presenter. Scripted responses do not become live AI after editing instructions. Gmail OAuth is an optional follow-up, not a requirement for these exercises.

## Before the session

1. Open a terminal in the workshop folder. Run `python -m venv .venv`, then `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`, then `.\.venv\Scripts\python.exe app.py` in PowerShell. Calling the executable directly avoids PowerShell activation-script policy changes.
2. Open the application at [http://127.0.0.1:8001/](http://127.0.0.1:8001/) and the deck at [http://127.0.0.1:8001/slides.html](http://127.0.0.1:8001/slides.html). If you open `static/slides.html` directly, the deck still works and the final demo link targets the local app.
3. Rehearse the guided walkthrough first. Say out loud that it is scripted and makes no AI calls.
4. For live agent execution, copy `.env.example` to `.env`, configure `GOOGLE_API_KEY`, leave `GMAIL_ENABLED=false`, and restart the server. That enables **Sample + Gemini** with fictional mail. `ADK_MODEL` selects the model. Check key access, model availability and quota before the audience arrives. Model calls can have costs. Retrieved email text and chat go to Gemini in both live modes.
5. Keep optional real Gmail out of the first exercise. If demonstrating it, follow the README's OAuth instructions, use an account you intend to connect and inspect the requested permissions. A Gemini key alone never authorises Gmail access.
6. Click **New private session** so previous proposals and saved preferences do not confuse the demo. Check the mode indicator after a reset or server restart. The mode comes from server settings. There is no browser mode switch.

On macOS or Linux, use `.venv/bin/python -m pip install -r requirements.txt` and `.venv/bin/python app.py` after creating the environment.

## Deck controls and editing

Use **Left/Right** or **Page Up/Page Down** for previous/next, **Home/End** for first/last, and **N** for presenter notes. The buttons provide the same controls. Notes appear in the same browser window, so hide them on the audience display when needed. A fragment such as `slides.html#10` opens a specific slide. Browser print shows all 19 slides in landscape format.

Edit text, diagrams and tables in `static/slides.html`, appearance in `static/slides.css`, and navigation in `static/slides.js`. The diagrams and tables are native HTML and remain editable. The cover illustration is `static/assets/inbox-hero.png`. No generated text is baked into the diagram.

## Demo walkthrough

The exact model reply can vary. Check the returned messages and pending actions instead of expecting a word-for-word answer.

1. **Mode:** Point to the current mode. **Guided walkthrough** is a scripted teaching fallback. **Sample + Gemini** is a real ADK agent using fictional inbox data. Optional **Gmail + Gemini** reads the authorised mailbox.
2. **Read:** Click or type “Summarize my inbox”. Show the email list. Expand **Scripted tool steps** in the walkthrough, or **Tool activity** in live mode. Explain that returned messages provide evidence for the summary.
3. **Priority and label:** Ask, “What needs my attention?” Open **Internship interview invitation** from **Recruitment Team** and compare the recommendation with its contents. The walkthrough also proposes a **Follow up** label. Inspect it and choose **Confirm label**, then verify it on the inbox message. In live mode, explicitly request that label if the agent has not proposed it. Treat draft approval and label approval as separate actions.
4. **Search:** In live mode, ask to find the interview email. Explain that search takes a query and returns matching messages. The walkthrough's draft flow already demonstrates a scripted search.
5. **Draft:** Ask, “Draft a reply to the interview email”. Inspect the recipient, subject and body. The scripted draft accepts Monday at 10 AM and asks for a meeting link. **Check your availability before accepting that time.** Show that a proposal has not saved a draft yet. Edit one sentence, choose **Confirm & save draft**, and open **Saved drafts** to verify the edited result. The app never sends email.
6. **Preference:** Ask, “Remember: keep replies concise”. Open **What Buddy remembers** to verify the preference. In live mode, request another draft and inspect the result. The preference belongs to this server session. It is not permanent model learning.
7. **Participant exercise:** Ask each participant to select one message, explain why it matters, request a draft and change a sentence before approval. In live mode, inspect a tool call. In the walkthrough, use the supplied demonstration flow because arbitrary prompts do not have live reasoning. The walkthrough always targets the sample interview for drafting.

If live AI fails, explain the actual error, clear `GOOGLE_API_KEY`, set `GMAIL_ENABLED=false` in `.env`, and restart the server to use the guided walkthrough. Say, “We are continuing with scripted examples.” Common live blockers include a missing or invalid key, unavailable model, exhausted quota and network access. If Gmail fails, set `GMAIL_ENABLED=false` and restart to continue with fictional mail. Return to OAuth setup after the session. Never present the fallback as a successful live ADK run.

## Accuracy reminders

- ADK is a framework. Gemini is the model used by this workshop's live mode.
- Codex and Claude Code can automate broader workflows, provide integrations and expose SDKs. They can help build this app. Avoid implying that email automation is unique to ADK.
- The comparison explains the benefit of owning a custom UI, tools, session rules and approval workflow. It makes no claim that ADK is smarter, faster or always cheaper.
- This implementation uses one agent with several tools. Multi-agent coordination is an optional concept on slide 12.
- The agent's write tools only propose actions. Separate server endpoints apply an explicitly approved draft or label. A prompt or email body cannot grant approval.
- The workshop's session storage is temporary. The upstream example's local memory file is a different design.
- Gmail uses the broad `gmail.modify` OAuth scope. The app's exposed tools do not send or delete messages. The absence of those operations in this app does not mean the OAuth permission only permits drafts.
- Real email bodies may contain private data or malicious instructions. Treat their text as data and use appropriate account permissions when extending the app.

## Projects to explore later

[Awesome ADK Agents](https://github.com/Sri-Krishna-V/awesome-adk-agents) is a community collection of project links. Use it to find an idea, then follow that project's own README. We reviewed the descriptions and links, but did not run these applications.

| Example | What it shows | Before trying it |
|---|---|---|
| [Trip planner](https://github.com/AashiDutt/Google-Agent-Development-Kit-Demo) | Flights, accommodation and activities | Read its setup and model-key instructions |
| [Voice calendar](https://github.com/bhancockio/adk-voice-agent) | Voice interaction with Google Calendar | Check microphone access, Calendar OAuth and model setup |
| [Voice-to-visualization](https://github.com/jenyss/google-adk-voice-to-visualization-agent) | Voice questions about Excel data produce charts | Check Gemini/OpenAI setup and audio/data dependencies |

The collection's older chart project, `jenyss/google-adk-data-visualization-agent`, says it no longer receives updates and points readers to `jenyss/google-adk-voice-to-visualization-agent`. The slide links the newer project. These examples are ideas for later exploration, not part of the inbox demo or a claim of production validation.

## Slide talk tracks and transitions

The following tracks match the deck's embedded notes. Adapt the wording to your audience.

### 1. Your first inbox agent

**Talk track:** Today we will explain what an agent is before touching code. We will use Google's Agent Development Kit, or ADK, to build an inbox assistant. By the end, you can read an inbox, ask for a reply draft and decide what the application saves. The illustration is generated workshop artwork, not a screenshot of the app.

**Transition:** First, what useful job do we want this assistant to do?

**Sources:** [Google ADK](https://adk.dev/). GDG mark from the supplied workshop design reference.

### 2. One inbox job

**Talk track:** An inbox is a useful learning example because the work is familiar. Reading and finding messages is different from changing your mailbox. The assistant can suggest a response, but the person remains responsible for the words and the action. This workshop deliberately has no sending tool.

**Transition:** How can a chat message cause the app to read an email?

**Sources:** [Original email-agent example](https://github.com/scspai/adk-email-agent). Approval flow: this workshop adaptation.

### 3. What an agent does

**Talk track:** A language model works with text. It cannot access our inbox just by writing an answer. A tool gives it a named operation, such as get_unread_emails. The model requests the operation and supplies arguments. Our Python function performs the operation and returns data. The model then uses that data to answer, or requests another tool. Some requests need no tools at all.

**Transition:** ADK provides the software that runs this cycle.

**Sources:** [ADK function tools](https://adk.dev/tools-custom/function-tools/), [ADK runtime](https://adk.dev/runtime/).

### 4. Google ADK

**Talk track:** A framework is reusable software that helps us build an application. ADK stands for Agent Development Kit. It gives us a place to define the agent and a runtime to operate it. A runner handles a conversation turn. A session groups the conversation and its state. ADK also provides development interfaces and evaluation support. Today our app supplies a custom inbox interface around that framework.

**Transition:** The framework and the model have different jobs.

**Sources:** [ADK overview](https://adk.dev/), [ADK runtime](https://adk.dev/runtime/), [ADK conversational context](https://adk.dev/sessions/).

### 5. AI model and toolkit

**Talk track:** People often mix up these names. Gemini is the model we use in the real AI mode. ADK is the surrounding agent framework. Changing the framework does not automatically improve the model's reasoning. We can improve tool design, provide better instructions and test useful examples. ADK also supports other model integrations. We stay with Gemini here to keep setup small.

**Transition:** Let's follow one request through our application.

**Sources:** [ADK overview and model support](https://adk.dev/).

### 6. One request through the app

**Talk track:** The browser is our user interface. It sends a message to our Python server. The ADK runner gives the model the message, context and tool definitions. Gemini may request get_unread_emails. Our function reads either fictional messages or an authorised Gmail inbox. Its result returns through the runtime. The model can now summarise actual returned data. Tool activity is observable, but we should not call that a transcript of private reasoning.

**Transition:** The agent definition that connects these pieces is small.

**Sources:** [ADK runtime](https://adk.dev/runtime/), [ADK function tools](https://adk.dev/tools-custom/function-tools/). Browser and trace: workshop app.

### 7. The agent definition

**Talk track:** Read this from the bottom up if Python is new to you. The tools list supplies an ordinary bound function. The instruction describes the assistant's job. The model selects the provider model. LlmAgent means an agent that uses a language model. create_agent takes an inbox session and returns that definition. This is an abbreviated pattern from our factory, not the entire runnable app. The actual file has stronger instructions, all workshop tools, and an ADK_MODEL environment setting.

**Transition:** A tool still needs ordinary code and real permissions.

**Sources:** [ADK Python quickstart](https://adk.dev/get-started/python/), [Function tools](https://adk.dev/tools-custom/function-tools/). Working implementation: inbox_agent/agent.py.

### 8. Tools and access

**Talk track:** A tool has a clear name, typed inputs and a useful description. Those help the model choose it. The function validates input, performs the operation and returns data or an error. Authentication happens separately. A Gemini API key authorises model use. Gmail OAuth is a user's consent to mailbox access. The model cannot create those permissions. Our default fictional inbox avoids OAuth entirely.

**Transition:** The app also needs to remember the current conversation.

**Sources:** [ADK function tools](https://adk.dev/tools-custom/function-tools/), [Gmail Python quickstart](https://developers.google.com/workspace/gmail/api/quickstart/python).

### 9. What this chat remembers

**Talk track:** A session gives related turns shared context. The model can understand a follow-up like 'make that shorter' because we keep the earlier conversation. Our preference tool stores a short-reply preference in the workshop session. This is not a model learning new weights, and it is not automatic permanent memory. Restarting the server clears the workshop's in-memory state. The upstream example uses a local memory file across sessions, which is a different storage choice.

**Transition:** Now we can compare the tool we are building with coding assistants you may already know.

**Sources:** [ADK conversational context](https://adk.dev/sessions/), [Upstream preference storage](https://github.com/scspai/adk-email-agent). Session lifetime: workshop implementation.

### 10. ADK, Codex and Claude Code

**Talk track:** These overlap, so this table compares starting points rather than exclusive capabilities. ADK is code for building our own agent application. Codex and Claude Code provide agents we can use directly for coding and other supported work. Both can be extended and expose SDKs. An SDK is a developer library that lets code use an agent. They are not limited to writing code. The choice depends on the interface, control and operating work we want to own. ADK adds application development and maintenance responsibilities. No comparison here claims a model-quality or price win.

**Transition:** For this inbox app, what makes owning the application useful?

**Sources:** [Google ADK](https://adk.dev/), [OpenAI code generation](https://developers.openai.com/api/docs/guides/code-generation), [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk), [Claude Code overview](https://code.claude.com/docs/en/overview). Ownership comparison is workshop interpretation, not an exclusive feature claim.

### 11. Why build your own app?

**Talk track:** Our users should see emails and an editable draft, rather than needing a developer terminal. A custom application lets us choose that interface. We also choose the functions the model can request and implement an approval boundary in ordinary code. ADK makes that agent application approachable. Other SDKs can also support custom applications. The advantage here is a fit to our chosen product architecture, not an exclusive ability. We still own authentication, deployment, quotas and failures. Coding assistants can help us write and review this app.

**Transition:** A custom application does not require a team of agents.

**Sources:** [ADK runtime](https://adk.dev/runtime/), [ADK tools](https://adk.dev/tools-custom/function-tools/), [Codex](https://developers.openai.com/api/docs/guides/code-generation), [Claude Code](https://code.claude.com/docs/en/overview). Product tradeoffs are workshop interpretation.

### 12. One agent first

**Talk track:** We do not need a separate agent for every function. One agent can decide among several tools. ADK also supports multi-agent and workflow patterns. A later version might separate classification from reply drafting, if different roles, evaluation needs or workflow constraints justify it. That is a conceptual extension, not a feature in today's app. More agents add coordination work and can add model calls.

**Transition:** Here is the actual scope of the demo we will run.

**Sources:** [ADK multi-agent support](https://adk.dev/). One-agent architecture: workshop implementation.

### 13. Meet Inbox Buddy

**Talk track:** The original SCSP example demonstrates unread Gmail access, labels, drafts and preferences. We adapt those ideas for a beginner workshop. Our agent can read and search, propose a draft or label, and store a preference in the session. The browser shows pending changes. The user edits and explicitly approves them. The server performs the approved operation. This makes the approval boundary visible and gives us a repeatable fictional inbox for teaching.

**Transition:** The same teaching app offers a path from a scripted rehearsal to real Gmail.

**Sources:** [SCSP ADK email agent](https://github.com/scspai/adk-email-agent). Additional search, UI and approval design: workshop adaptation.

### 14. Demo modes

**Talk track:** We start with the guided walkthrough so everyone can practice the interface. Its replies are scripted and it does not make an AI call. Sample + Gemini calls a real ADK agent, but tools still use fictional emails. That isolates agent learning from Gmail setup. Gmail + Gemini adds an optional real mailbox adapter after OAuth. Both live modes send chat and retrieved email text to Gemini. The server chooses the mode from .env at startup. There is no browser mode switch. Always read the mode indicator before presenting results.

**Transition:** In every mode, the approval flow stays the same.

**Sources:** Mode definitions: workshop implementation. [ADK key setup](https://adk.dev/get-started/python/), [Gmail OAuth setup](https://developers.google.com/workspace/gmail/api/quickstart/python).

### 15. You approve changes

**Talk track:** Telling the model to be careful is useful, but we also enforce the rule in the application. The exposed agent tools create proposals. They cannot directly save Gmail drafts or apply labels. A separate approval request from the browser asks the server to apply the pending change. The user can edit a draft before that request. There is no sending path. Malicious text inside an email is inbox data, not a new user command or approval. The approval control helps, but a production app would also need authentication, access controls and broader security review.

**Transition:** We can now run the app locally with a small setup.

**Sources:** Approval boundary and tool scope: inbox_agent/tools.py and app.py in this workshop. [Gmail drafts guide](https://developers.google.com/workspace/gmail/api/guides/drafts).

### 16. More agents to explore

**Talk track:** The Awesome ADK Agents repository is a collection of links, not one application to install. It is a useful place to find ideas after the workshop. The travel example plans flights, stays and activities. The voice example connects speech interaction with Google Calendar. The chart example takes voice requests about Excel data and produces charts. The collection links an older data-visualization repo whose README points readers to this newer voice-to-visualization version. Follow each project's README and check current dependencies, keys, OAuth and costs. We have read the examples, not run or certified them for production.

**Transition:** For now, we will run our small inbox app and try its four prompts.

**Sources:** [Awesome ADK Agents](https://github.com/Sri-Krishna-V/awesome-adk-agents), [Travel planner](https://github.com/AashiDutt/Google-Agent-Development-Kit-Demo), [Voice calendar agent](https://github.com/bhancockio/adk-voice-agent), [Voice-to-visualization agent](https://github.com/jenyss/google-adk-voice-to-visualization-agent).

### 17. Local setup

**Talk track:** A virtual environment keeps this project's packages together. We call its Python executable directly, so PowerShell does not need an activation-script policy change. requirements.txt lists the dependencies. app.py starts our local server. We use port 8001, not the default ADK development UI port. The guided walkthrough works without credentials. Copy .env.example to .env and place GOOGLE_API_KEY there for Sample + Gemini. Keep GMAIL_ENABLED=false for fictional mail. Restart the server after changing .env. Never paste it into a slide or chat prompt. Keep the model setting configurable because available models and quotas change.

**Transition:** Here is the short sequence we will demonstrate.

**Sources:** Workshop README and requirements.txt. [ADK Python quickstart](https://adk.dev/get-started/python/).

### 18. Live demo sequence

**Talk track:** Announce the mode first. Ask for unread messages, then priorities. Open 'Internship interview invitation' from Recruitment Team to check the source. The walkthrough proposes the Follow up label with the priority request. Inspect it and choose 'Confirm label'. Ask for a draft and show that the saved draft count has not changed yet. The scripted draft accepts Monday at 10 AM. Check availability and edit that sentence before choosing 'Confirm & save draft'. Finally use the preference prompt and open 'What Buddy remembers'. The guided walkthrough recognises only its scripted flow. In real AI mode, inspect tool activity when an answer differs. Request a label explicitly if the live agent has not proposed one.

**Transition:** We are ready to use the app. Keep the deck on this final demo slide.

**Sources:** This workshop's demo interface and fictional inbox.

### 19. Live inbox agent demo

**Talk track:** Open the local demo and finish the presentation in the application. Participants can choose the message that deserves attention, ask for a reply, and change one sentence before approving. Ask them to identify the model, framework, tool and approval boundary in what they just used. If there is time, restart with a Gemini key and compare the same request in the guided walkthrough and Sample + Gemini. A production extension should begin with a concrete user need and a test, rather than adding agents by default.

**Demo link:** The app must run at http://127.0.0.1:8001/. A file-based deck redirects the demo link there. A served deck uses the current server's root.

**Sources:** [Workshop fork](https://github.com/Chee613/gdg-adk-workshop), [Upstream example](https://github.com/scspai/adk-email-agent), [Google ADK](https://adk.dev/).
