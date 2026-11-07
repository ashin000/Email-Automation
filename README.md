# MailMind AI — Intelligent Email Assistant

An email intelligence assistant built with Python, the Gemini API, Gmail API, SQLite, Telegram and Playwright.

## Features
- Read-only Gmail ingestion using the official Gmail API.
- Gemini-powered email classification and concise summaries.
- Categories: Important, Newsletter, Promotional, General.
- Optional Telegram alerts for Important messages.
- SQLite deduplication to prevent repeated notifications.
- Optional Playwright browser automation demo.
- Safe by default: no deleting, archiving, replying to, or forwarding email.

**Why Gmail API instead of Playwright to read Gmail?** Gmail's UI changes frequently. The official read-only API is more reliable for mailbox access. Playwright remains included for permitted browser workflows and learning.

## Requirements
- Python 3.10+
- Gemini API key
- Google Cloud project with Gmail API enabled and OAuth Desktop credentials
- Optional Telegram bot

## Windows setup
```powershell
git clone https://github.com/ashin000/Email-Automation.git
cd Email-Automation
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Configure Gemini
1. Open https://aistudio.google.com/apikey and create a Gemini API key.
2. Open the project's `.env` file.
3. Set `GEMINI_API_KEY=your_api_key`.
4. Keep the key private; never commit `.env` to GitHub.

The default model is `gemini-2.5-flash`. You can change it with `GEMINI_MODEL`. The application uses Google's official `google-genai` Python SDK and requests structured JSON output for predictable classification.

Test Gemini without connecting Gmail:
```powershell
python -m app.main --test-ai
```

## Gmail OAuth setup
1. Create/select a project at https://console.cloud.google.com/.
2. Enable Gmail API.
3. Configure the OAuth consent screen and add your Google account as a test user if needed.
4. Create OAuth client credentials of type **Desktop app**.
5. Download the JSON to the project root as `credentials.json`.
6. Run `python -m app.main --once`. The first run opens Google consent and creates `token.json`.

The app requests only `gmail.readonly`. Both OAuth files are excluded from Git.

## Telegram setup (optional)
Create a bot with Telegram's BotFather, start a chat with it, and set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, and `TELEGRAM_ENABLED=true` in `.env`.

## Run
One scan:
```powershell
python -m app.main --once
```
Continuous polling (default every 5 minutes):
```powershell
python -m app.main
```
AI-only test:
```powershell
python -m app.main --test-ai
```

## Playwright demo
```powershell
playwright install chromium
python -m app.browser_demo
```
The demo visits example.com and extracts its heading. It does not log in to Gmail or handle account credentials.

## Deployment
Deploy on a persistent Python host (Linux VPS or home server). Install Python and Git, clone the repo, install dependencies, configure `.env`, securely provision Google OAuth files, then run under systemd or Docker with persistent storage for `data/` and OAuth token. Gemini inference uses the hosted Gemini API, so the server needs outbound internet access and a valid API key; Ollama is not required. Complete Gmail OAuth interactively on a trusted machine first if the server has no browser, then transfer the token securely.

## Security
- Gmail scope is read-only.
- Email body is treated as untrusted data in the classifier prompt.
- Email content is sent to Google's Gemini API for classification and summarization; review Google's API data-use and retention terms before processing sensitive mailbox content.
- When enabled, summaries are sent to Telegram.
- Never commit `.env`, API keys, `credentials.json`, `token.json`, database files, logs or browser profiles.

Starter implementation; test Gemini, Gmail OAuth and Telegram configuration in your environment before unattended operation.
