import logging
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from google_auth_oauthlib.flow import InstalledAppFlow

from app.config import settings
from app.database import get_dashboard_data
from app.gmail_reader import get_gmail_profile
from app.main import process_batch

app = FastAPI(title="MailMind Product MVP")
logger = logging.getLogger(__name__)
_scan_status = {"state": "idle", "processed": 0, "failed": 0}


def _save_credentials(credentials, token_file: Path) -> None:
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(credentials.to_json(), encoding="utf-8")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "mailmind-product-mvp"}


def _scan_after_login() -> None:
    _scan_status.update({"state": "running", "processed": 0, "failed": 0})
    try:
        result = process_batch()
        _scan_status.update({
            "state": "partial" if result["failed"] else "complete",
            "processed": result["processed"],
            "failed": result["failed"],
        })
    except Exception:
        logger.exception("Inbox scan failed after Google login")
        _scan_status.update({"state": "error", "processed": 0, "failed": 1})


def _queue_scan(background_tasks: BackgroundTasks) -> None:
    _scan_status.update({"state": "queued", "processed": 0, "failed": 0})
    background_tasks.add_task(_scan_after_login)


@app.get("/api/dashboard")
def dashboard_data():
    connected = settings.gmail_token_file.exists()
    data = get_dashboard_data()
    email_address = None
    if connected:
        try:
            email_address = get_gmail_profile().get("emailAddress")
        except Exception:
            logger.exception("Could not read the connected Gmail profile")

    data.update({
        "connected": connected,
        "user": {"email": email_address},
        "scan": dict(_scan_status),
        "telegram_configured": bool(
            settings.telegram_enabled and settings.telegram_bot_token and settings.telegram_chat_id
        ),
    })
    return data


@app.post("/api/scan")
def scan_inbox(background_tasks: BackgroundTasks):
    if not settings.gmail_token_file.exists():
        return JSONResponse(
            status_code=400,
            content={"message": "Connect your Gmail account before scanning the inbox."},
        )
    if _scan_status["state"] in {"queued", "running"}:
        return JSONResponse(status_code=409, content={"message": "An inbox scan is already running."})

    _queue_scan(background_tasks)
    return {"status": "queued", "message": "Inbox analysis started."}


@app.get("/api/oauth/google")
def google_oauth_start(background_tasks: BackgroundTasks):
    credentials_file = settings.gmail_credentials_file
    if not credentials_file.exists():
        return JSONResponse(
            status_code=400,
            content={
                "message": "Missing credentials.json. Create OAuth Desktop credentials in Google Cloud Console first.",
                "next_step": "Download the JSON file and save it at the project root as credentials.json",
            },
        )

    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), scopes=SCOPES)
        credentials = flow.run_local_server(port=0)
        token_file = settings.gmail_token_file
        _save_credentials(credentials, token_file)
        _queue_scan(background_tasks)
        return RedirectResponse(url="/?connected=1", status_code=302)
    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Google OAuth failed.",
                "error": str(exc),
            },
        )


@app.get("/api/oauth/google/callback")
def google_oauth_callback(request: Request):
    if "code" not in request.query_params:
        return JSONResponse(
            status_code=400,
            content={"message": "This callback is handled by the Google installed-app login flow. Use /api/oauth/google to begin sign-in."},
        )

    return JSONResponse(
        status_code=400,
        content={
            "message": "Google returned a callback code, but the app is using the installed-app flow. The code must be exchanged by Google OAuth on the local desktop flow, not by a custom callback endpoint.",
            "error": "redirect_uri_mismatch",
        },
    )


@app.get("/api/user-summary/{user_id}")
def user_summary(user_id: str):
    return {
        "user_id": user_id,
        "status": "ready_for_oauth",
        "summary": "This endpoint will return the authenticated user’s inbox summary once Gmail OAuth is connected.",
    }


@app.get("/", response_class=HTMLResponse)
def index():
    html = Path(__file__).resolve().parent.parent / "web" / "index.html"
    return html.read_text(encoding="utf-8")
