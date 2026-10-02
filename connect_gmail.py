"""Explicit, local OAuth setup; never triggered automatically from chat."""
from inbox_agent.gmail import BASE_DIR, SCOPES


def main():
    from google_auth_oauthlib.flow import InstalledAppFlow
    source = BASE_DIR / "credentials.json"
    if not source.exists():
        raise SystemExit("Download Desktop OAuth credentials as credentials.json first. See README.md.")
    print("Opening Google sign-in. Gmail text can reach Gemini when GMAIL_ENABLED=true.")
    flow = InstalledAppFlow.from_client_secrets_file(str(source), SCOPES)
    credentials = flow.run_local_server(port=0)
    (BASE_DIR / "token.json").write_text(credentials.to_json(), encoding="utf-8")
    print("Connected. Set GMAIL_ENABLED=true in .env and restart python app.py.")


if __name__ == "__main__":
    main()
