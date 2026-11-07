from app.models import EmailAnalysis, EmailMessage

def test_email_message_model():
    item = EmailMessage("abc", "sender@example.com", "Subject", "Body")
    assert item.message_id == "abc"

def test_analysis_model():
    result = EmailAnalysis("Important", "High", "Transaction alert")
    assert result.category == "Important"
