"""Environment-backed configuration."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

@dataclass(frozen=True)
class Settings:
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    gmail_credentials_file: Path = ROOT / os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
    gmail_token_file: Path = ROOT / os.getenv("GMAIL_TOKEN_FILE", "token.json")
    gmail_query: str = os.getenv("GMAIL_QUERY", "is:unread in:inbox")
    gmail_max_results: int = int(os.getenv("GMAIL_MAX_RESULTS", "25"))
    telegram_enabled: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    telegram_only_important: bool = os.getenv("TELEGRAM_ONLY_IMPORTANT", "true").lower() == "true"
    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
    database_path: Path = ROOT / os.getenv("DATABASE_PATH", "data/mailmind.sqlite3")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

settings = Settings()
