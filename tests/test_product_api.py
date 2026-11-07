from pathlib import Path

from fastapi.testclient import TestClient

from app.config import settings
from app.database import save_analysis
from app.models import EmailAnalysis, EmailMessage
import app.product_api as product_api
from app.product_api import app


client = TestClient(app)


def test_google_oauth_requires_credentials_file(tmp_path):
    original = settings.gmail_credentials_file
    object.__setattr__(settings, "gmail_credentials_file", tmp_path / "missing.json")
    try:
        response = client.get("/api/oauth/google", follow_redirects=False)
    finally:
        object.__setattr__(settings, "gmail_credentials_file", original)

    assert response.status_code == 400
    assert "credentials.json" in response.json()["message"]


def test_google_oauth_callback_fails_gracefully_on_invalid_code():
    response = client.get("/api/oauth/google/callback?code=not-valid", follow_redirects=False)

    assert response.status_code != 500
    assert response.status_code in (400, 302)


def test_dashboard_is_empty_before_gmail_is_connected(tmp_path):
    original_database = settings.database_path
    original_token = settings.gmail_token_file
    object.__setattr__(settings, "database_path", tmp_path / "dashboard.sqlite3")
    object.__setattr__(settings, "gmail_token_file", tmp_path / "missing-token.json")
    try:
        response = client.get("/api/dashboard")
    finally:
        object.__setattr__(settings, "database_path", original_database)
        object.__setattr__(settings, "gmail_token_file", original_token)

    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is False
    assert data["totals"]["analyzed"] == 0
    assert data["recent"] == []


def test_dashboard_uses_saved_real_analysis(tmp_path, monkeypatch):
    original_database = settings.database_path
    original_token = settings.gmail_token_file
    object.__setattr__(settings, "database_path", tmp_path / "dashboard.sqlite3")
    object.__setattr__(settings, "gmail_token_file", tmp_path / "token.json")
    settings.gmail_token_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(product_api, "get_gmail_profile", lambda: {"emailAddress": "person@example.com"})
    try:
        save_analysis(
            EmailMessage("mail-1", "sender@example.com", "Invoice due", "Please review"),
            EmailAnalysis("Important", "High", "An invoice needs review.", "Payment deadline"),
        )
        response = client.get("/api/dashboard")
    finally:
        object.__setattr__(settings, "database_path", original_database)
        object.__setattr__(settings, "gmail_token_file", original_token)

    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert data["user"]["email"] == "person@example.com"
    assert data["totals"]["analyzed"] == 1
    assert data["totals"]["important"] == 1
    assert data["recent"][0]["subject"] == "Invoice due"


def test_manual_scan_queues_existing_gmail_token(tmp_path, monkeypatch):
    original_token = settings.gmail_token_file
    object.__setattr__(settings, "gmail_token_file", tmp_path / "token.json")
    settings.gmail_token_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(product_api, "process_batch", lambda: {"processed": 2, "failed": 0})
    product_api._scan_status.update({"state": "idle", "processed": 0, "failed": 0})
    try:
        response = client.post("/api/scan")
    finally:
        object.__setattr__(settings, "gmail_token_file", original_token)

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    assert product_api._scan_status == {"state": "complete", "processed": 2, "failed": 0}
