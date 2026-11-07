"""Shared email models."""
from dataclasses import dataclass

@dataclass
class EmailMessage:
    message_id: str
    sender: str
    subject: str
    body: str
    received_at: str = ""
    snippet: str = ""

@dataclass
class EmailAnalysis:
    category: str
    priority: str
    summary: str
    reasons: str = ""
