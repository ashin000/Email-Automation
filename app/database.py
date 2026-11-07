"""SQLite storage and deduplication."""
import sqlite3
from app.config import settings
from app.models import EmailAnalysis, EmailMessage

def _connect():
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS processed_emails (
        message_id TEXT PRIMARY KEY, sender TEXT NOT NULL, subject TEXT NOT NULL,
        category TEXT NOT NULL, priority TEXT NOT NULL, summary TEXT NOT NULL,
        processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    return conn

def is_processed(message_id: str) -> bool:
    with _connect() as conn:
        return conn.execute("SELECT 1 FROM processed_emails WHERE message_id=?", (message_id,)).fetchone() is not None

def save_analysis(email: EmailMessage, analysis: EmailAnalysis) -> bool:
    with _connect() as conn:
        cur = conn.execute("INSERT OR IGNORE INTO processed_emails(message_id,sender,subject,category,priority,summary) VALUES(?,?,?,?,?,?)",
            (email.message_id,email.sender,email.subject,analysis.category,analysis.priority,analysis.summary))
        return cur.rowcount == 1
