# MailMind AI — Intelligent Email Assistant

A local-first email intelligence assistant built with Python, Ollama, Gmail API, SQLite, Telegram and Playwright.

## Features
- Read-only Gmail ingestion using the official Gmail API.
- Ollama-powered classification and concise summaries.
- Categories: Important, Newsletter, Promotional, General.
- Optional Telegram alerts for Important messages.
- SQLite deduplication to prevent repeated notifications.
- Optional Playwright browser automation demo.
- Safe by default: no deleting, archiving, replying to, or forwarding email.

**Why Gmail API instead of Playwright to read Gmail?** Gmail's UI changes frequently. The official read-only API is more reliable for mailbox access. Playwright remains included for permitted browser workflows and learning.

## Requirements
- Python 3.10+
- Ollama installed and running
- Model such as `qwen2.5:3b`
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

Install Ollama from https://ollama.com/download, then:
```powershell
ollama pull qwen2.5:3b
ollama serve
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
Use an always-on Linux VPS or home server because Ollama needs a persistent local model runtime. Install Python, Git and Ollama; clone the repo; install dependencies; pull the model; configure `.env`; securely provision Google OAuth files; then run under systemd or Docker with persistent storage for `data/`, OAuth token and Ollama models. Complete OAuth interactively on a trusted machine first if the server has no browser, then transfer the token securely. Never expose Ollama's local API publicly.

## Security
- Gmail scope is read-only.
- Email body is treated as untrusted data in the classifier prompt.
- No email content is sent to a hosted AI provider; local Ollama handles inference.
- When enabled, summaries are sent to Telegram.
- Never commit `.env`, `credentials.json`, `token.json`, database files, logs or browser profiles.

Starter implementation; test OAuth, Ollama and Telegram in your environment before unattended operation.
