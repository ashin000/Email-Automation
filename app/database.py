"""SQLite storage and deduplication."""
import sqlite3
from collections import Counter

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

def get_dashboard_data() -> dict:
    """Build dashboard totals and recent messages from saved analyses."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT sender,subject,category,priority,summary,processed_at "
            "FROM processed_emails ORDER BY processed_at DESC"
        ).fetchall()

    counts = Counter(row[2] for row in rows)
    categories = ("Important", "Newsletter", "Promotional", "General")
    summaries = []
    for category in categories:
        items = [row for row in rows if row[2] == category]
        summaries.append({
            "category": category,
            "count": counts[category],
            "summary": items[0][4] if items else "No analyzed messages in this category yet.",
        })

    recent = [
        {
            "from": sender,
            "subject": subject,
            "category": category,
            "priority": priority,
            "summary": summary,
            "processed_at": processed_at,
        }
        for sender, subject, category, priority, summary, processed_at in rows[:20]
    ]
    return {
        "totals": {
            "analyzed": len(rows),
            "important": counts["Important"],
            "newsletter": counts["Newsletter"],
            "promotional": counts["Promotional"],
            "general": counts["General"],
        },
        "summary": summaries,
        "recent": recent,
    }
