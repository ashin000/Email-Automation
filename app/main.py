"""MailMind AI command-line entry point."""
import argparse
import logging
import time
from app.ai_analyzer import analyze_email
from app.config import settings
from app.database import is_processed, save_analysis
from app.gmail_reader import fetch_unread_emails
from app.models import EmailMessage
from app.telegram_bot import send_email_notification

def process_batch():
    log = logging.getLogger(__name__)
    emails = fetch_unread_emails()
    log.info("Fetched %d message(s)", len(emails))
    count = 0
    for email in emails:
        if is_processed(email.message_id):
            continue
        try:
            analysis = analyze_email(email)
            if save_analysis(email, analysis):
                send_email_notification(email, analysis)
                log.info("Processed [%s / %s] %s", analysis.category, analysis.priority, email.subject)
                count += 1
        except Exception:
            log.exception("Could not process message %s", email.message_id)
    log.info("New messages processed: %d", count)

def main():
    parser = argparse.ArgumentParser(description="MailMind AI email intelligence assistant")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="Scan inbox once")
    mode.add_argument("--test-ai", action="store_true", help="Test Ollama without Gmail")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.test_ai:
        sample = EmailMessage("demo","alerts@examplebank.com","Debit transaction alert","A debit of INR 2500 was made on your bank account today. Contact the bank if this was not you.")
        print(analyze_email(sample))
    elif args.once:
        process_batch()
    else:
        logging.getLogger(__name__).info("Polling every %s seconds", settings.poll_interval_seconds)
        while True:
            try:
                process_batch()
            except Exception:
                logging.getLogger(__name__).exception("Polling cycle failed")
            time.sleep(max(30, settings.poll_interval_seconds))

if __name__ == "__main__":
    main()
