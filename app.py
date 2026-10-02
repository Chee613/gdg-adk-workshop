"""Local workshop server: python app.py, then http://127.0.0.1:8001."""
import asyncio
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field

from inbox_agent.tools import InboxSession

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
app = FastAPI(title="Inbox Buddy", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"])
sessions = {}


@app.middleware("http")
async def local_only(request: Request, call_next):
    # Reject cross-site requests and oversized payloads before parsing or starting an agent.
    origin = request.headers.get("origin")
    expected = f"{request.url.scheme}://{request.headers.get('host', '')}"
    if request.url.path.startswith("/api/"):
        if origin and origin != expected:
            return JSONResponse({"detail": "Open Inbox Buddy directly in its local browser tab."}, status_code=403)
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse({"detail": "Cross-site requests are not accepted."}, status_code=403)
        size = request.headers.get("content-length", "0")
        if not size.isdigit() or int(size) > 40000:
            return JSONResponse({"detail": "Request is too large."}, status_code=413)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


class Chat(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class Approval(BaseModel):
    body: str | None = Field(default=None, min_length=1, max_length=8000)


def session_for(request):
    found = sessions.get(request.headers.get("X-Session-ID"))
    if not found:
        raise HTTPException(401, "Your session expired. Start a new demo session.")
    return found


@app.post("/api/session")
async def new_session():
    key = bool(os.getenv("GOOGLE_API_KEY", "").strip())
    live = os.getenv("GMAIL_ENABLED", "false").lower() == "true"
    if live and not key:
        raise HTTPException(400, "Gmail mode requires a Gemini API key. Set GMAIL_ENABLED=false for the sample walkthrough.")
    if live and not (BASE_DIR / "token.json").exists():
        raise HTTPException(400, "Run python connect_gmail.py to connect Gmail, or set GMAIL_ENABLED=false.")
    mode = "gmail-ai" if live else "sample-ai" if key else "walkthrough"
    sid = secrets.token_urlsafe(32)
    inbox = InboxSession(live=live)
    entry = {"inbox": inbox, "lock": asyncio.Lock(), "runner": None}
    if key:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from inbox_agent.agent import create_agent
        service = InMemorySessionService()
        await service.create_session(app_name="inbox_buddy", user_id=sid, session_id=sid)
        entry["runner"] = Runner(agent=create_agent(inbox), app_name="inbox_buddy", session_service=service)
    # ponytail: local workshop, 32 in-memory sessions; use durable session storage for a hosted app.
    if len(sessions) >= 32:
        sessions.pop(next(iter(sessions)))
    sessions[sid] = entry
    return {"session_id": sid, "mode": mode,
            "engine": "Google ADK + Gemini" if key else "Scripted walkthrough (no AI model)", **inbox.snapshot()}


@app.get("/api/state")
async def state(request: Request):
    return session_for(request)["inbox"].snapshot()


@app.post("/api/chat")
async def chat(request: Request, payload: Chat):
    entry = session_for(request)
    if not payload.message.strip():
        raise HTTPException(400, "Type a message first.")
    if entry["lock"].locked():
        raise HTTPException(409, "Wait for the current request to finish.")
    async with entry["lock"]:
        inbox = entry["inbox"]
        inbox.activity = []
        if not entry["runner"]:
            try:
                reply = inbox.walkthrough(payload.message)
            except ValueError as error:
                raise HTTPException(400, str(error)) from error
        else:
            from google.genai import types
            from google.adk.agents.run_config import RunConfig
            response = []
            try:
                async with asyncio.timeout(75):
                    sid = request.headers["X-Session-ID"]
                    async for event in entry["runner"].run_async(
                        user_id=sid, session_id=sid,
                        new_message=types.Content(role="user", parts=[types.Part(text=payload.message)]),
                        run_config=RunConfig(max_llm_calls=12),
                    ):
                        if event.is_final_response() and event.content:
                            response.extend(p.text for p in event.content.parts or [] if p.text and not p.thought)
                reply = "\n".join(response) or "Review any prepared suggestions below."
            except Exception as error:
                # Error text from providers can include request details; do not expose it in the UI.
                print(f"ADK request failed: {type(error).__name__}")
                return JSONResponse({"detail": "Gemini could not finish this request. Check your API key, model and quota. Review any prepared suggestions before retrying.",
                                     "activity": inbox.activity, **inbox.snapshot()}, status_code=502)
        return {"reply": reply, "activity": inbox.activity, **inbox.snapshot()}


@app.post("/api/actions/{action_id}/approve")
async def approve(action_id: str, request: Request, payload: Approval):
    entry = session_for(request)
    if entry["lock"].locked():
        raise HTTPException(409, "Wait for the current request to finish.")
    async with entry["lock"]:
        inbox = entry["inbox"]
        inbox.activity = []
        try:
            action = await asyncio.to_thread(inbox.approve, action_id, payload.body)
        except ValueError as error:
            raise HTTPException(400, str(error)) from error
        except Exception as error:
            print(f"Gmail approval failed: {type(error).__name__}")
            raise HTTPException(502, "Could not confirm the Gmail action. Check Gmail before retrying; your review suggestion is still available.") from error
        reply = "Draft saved. Nothing was sent." if action["kind"] == "draft" else "Your approved label is applied."
        return {"reply": reply, "activity": inbox.activity, **inbox.snapshot()}


@app.post("/api/actions/{action_id}/decline")
async def decline(action_id: str, request: Request):
    entry = session_for(request)
    if entry["lock"].locked():
        raise HTTPException(409, "Wait for the current request to finish.")
    inbox = entry["inbox"]
    inbox.activity = []
    try:
        inbox.decline(action_id)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error
    return {"reply": "Suggestion discarded. Nothing changed in your inbox.", "activity": inbox.activity, **inbox.snapshot()}


app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
