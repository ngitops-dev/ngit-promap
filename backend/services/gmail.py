import base64
from email.mime.text import MIMEText

from backend.config import settings
from backend.services.google_auth import get_gmail_service
from backend.utils.logging import get_logger

logger = get_logger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    if not settings.GMAIL_SENDER:
        logger.error("GMAIL_SENDER not configured")
        return False

    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message["to"] = to
        message["from"] = settings.GMAIL_SENDER
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        logger.info("Email sent to %s | subject=%s", to, subject)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s | error=%s", to, str(e))
        return False


def send_html_email(to: str, subject: str, html_body: str) -> bool:
    if not settings.GMAIL_SENDER:
        logger.error("GMAIL_SENDER not configured")
        return False

    try:
        service = get_gmail_service()
        message = MIMEText(html_body, "html")
        message["to"] = to
        message["from"] = settings.GMAIL_SENDER
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
        service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        logger.info("HTML email sent to %s | subject=%s", to, subject)
        return True
    except Exception as e:
        logger.error("Failed to send HTML email to %s | error=%s", to, str(e))
        return False
