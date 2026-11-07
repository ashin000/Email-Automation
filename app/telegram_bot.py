"""Optional Telegram notification sender."""
import logging
import requests
from app.config import settings
from app.models import EmailAnalysis, EmailMessage

logger = logging.getLogger(__name__)

def _escape(value: str) -> str:
    return value.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def send_email_notification(email: EmailMessage, analysis: EmailAnalysis) -> bool:
    if not settings.telegram_enabled:
        return False
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram enabled but token/chat ID is missing")
        return False
    if settings.telegram_only_important and analysis.category != "Important":
        return False
    text = ("✉️ <b>MailMind AI — Email Alert</b>\n\n"
        f"<b>Category:</b> {_escape(analysis.category)}\n"
        f"<b>Priority:</b> {_escape(analysis.priority)}\n"
        f"<b>From:</b> {_escape(email.sender)}\n"
        f"<b>Subject:</b> {_escape(email.subject)}\n\n"
        f"<b>Summary:</b> {_escape(analysis.summary)}")
    try:
        response = requests.post(f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json={"chat_id":settings.telegram_chat_id,"text":text,"parse_mode":"HTML","disable_web_page_preview":True},timeout=20)
        response.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("Telegram send failed")
        return False
