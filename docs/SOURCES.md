# Workshop sources

Primary references checked on 2 October 2026. The slides include relevant citations in their presenter notes. Official product pages can change. Model availability, quotas and costs should be checked again before presenting.

| Source | Supports | Slides |
|---|---|---|
| [Google ADK](https://adk.dev/) | Open-source toolkit, model integrations, development and support for teams of agents | 1, 4, 5, 10, 12, 19 |
| [ADK Python quickstart](https://adk.dev/get-started/python/) | Python installation, basic agent definition and API-key setup | 7, 14, 17 |
| [ADK function tools](https://adk.dev/tools-custom/function-tools/) | Ordinary functions as tools, arguments and returned results | 3, 6, 7, 8, 11 |
| [ADK runtime](https://adk.dev/runtime/) | Runner, conversation turns and tool execution | 3, 4, 6, 11 |
| [ADK conversational context](https://adk.dev/sessions/) | Session, state and memory distinctions | 4, 9 |
| [OpenAI code generation](https://developers.openai.com/api/docs/guides/code-generation) | Codex as an agent and programmable coding workflows | 10, 11 |
| [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk) | Codex integration in custom workflows | 10 |
| [Claude Code overview](https://code.claude.com/docs/en/overview) | Coding/work agent, integrations and Agent SDK | 10, 11 |
| [SCSP ADK email-agent repository](https://github.com/scspai/adk-email-agent) | Original Gmail read, label, draft and preference example | 2, 9, 13, 19 |
| [Gmail Python quickstart](https://developers.google.com/workspace/gmail/api/quickstart/python) | Gmail API and separate OAuth authorisation | 8, 14 |
| [Gmail drafts guide](https://developers.google.com/workspace/gmail/api/guides/drafts) | Draft resources and draft operations | 15 |
| [Workshop fork](https://github.com/Chee613/gdg-adk-workshop) | This adaptation's UI, modes, tool scope and approval behaviour | 13–19 |
| [Awesome ADK Agents](https://github.com/Sri-Krishna-V/awesome-adk-agents) | A collection to discover community projects | 16 |
| [AashiDutt travel planner](https://github.com/AashiDutt/Google-Agent-Development-Kit-Demo) | Travel example covering flights, stays and activities | 16 |
| [Brandon Hancock voice agent](https://github.com/bhancockio/adk-voice-agent) | Voice interaction and Google Calendar integration | 16 |
| [Jenyss voice-to-visualization](https://github.com/jenyss/google-adk-voice-to-visualization-agent) | Voice requests about Excel data and chart output | 16 |

## Attribution and adaptations

The application adapts [scspai/adk-email-agent](https://github.com/scspai/adk-email-agent), distributed under Apache License 2.0. Its original files are retained in `upstream-reference/`. See the root `LICENSE` and project README for code attribution. The workshop adds a custom inbox UI, fictional mail, a scripted guided walkthrough, live ADK modes, search and an explicit application approval flow.

The reference implementation stores preferences in a local file. This workshop uses temporary session storage. The reference agent can call Gmail draft and label operations as tools. This workshop instead exposes proposal tools and performs those changes through separate approval requests. These are intentional changes for teaching and should not be attributed to the upstream implementation.

The ADK/Codex/Claude Code comparison is a workshop interpretation of their documented starting points. Capabilities overlap. No source establishes a universal quality or cost ranking, and the deck makes no such claim.

The community examples are references to explore, not applications we installed or certified. Awesome ADK Agents links the older `jenyss/google-adk-data-visualization-agent`; that project's README directs readers to the newer voice-to-visualization project used on slide 16. Each linked project has separate setup and dependencies.

## Visual assets

- `static/assets/gdg-mark-reference.png`: unchanged GDG mark copied from the user's supplied `gdg-slide-design` skill reference. Preserve its proportions and Google colours.
- `static/assets/inbox-hero.png`: generated workshop illustration. Prompt direction: ivory ceramic/clay miniature inbox, colourful envelopes, friendly assistant, restrained Google-colour accents, daylight and a white backdrop. It is illustrative artwork, not a photograph or app screenshot.
- `static/assets/agent-toolkit.png`: generated ceramic assistant, speech bubble, gear, tool blocks and envelope. Used to explain the ADK toolkit and the custom app.
- `static/assets/explore-projects.png`: generated ceramic travel, voice/calendar and spreadsheet/chart objects. Used beside the linked community examples. See `docs/ARTWORK.md` for prompt provenance.
- Layout follows the supplied `gdg-slide-design` reference: white 16:9 frame, pale surrounding grid, large Google Sans typography, Google colours and flat editable explanations.

All important explanatory text, process labels and comparison tables remain native HTML. The slides do not use rasterised text for factual content.
