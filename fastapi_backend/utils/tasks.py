import logging
import smtplib
from email.message import EmailMessage
from typing import Any

from .celery_app import celery
from config import settings
from .redis_cache import get_sync_redis, delete_pattern_sync

logger = logging.getLogger(__name__)


def _send_email(subject: str, body: str, recipient: str) -> None:
    if not settings.SMTP_HOST:
        logger.warning("SMTP_HOST is not configured. Skipping email to %s", recipient)
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                smtp.starttls()
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
            logger.info("Sent email to %s", recipient)
    except Exception as exc:
        logger.exception("Failed to send email to %s: %s", recipient, exc)


@celery.task(name="tasks.invalidate_cache_prefix")
def invalidate_cache_prefix(prefix: str) -> dict[str, Any]:
    deleted = delete_pattern_sync(f"{prefix}*")
    logger.info("Invalidated cache prefix %s (deleted %s keys)", prefix, deleted)
    return {"prefix": prefix, "deleted": deleted}


@celery.task(name="tasks.send_welcome_email")
def send_welcome_email(email_address: str, username: str) -> dict[str, str]:
    subject = "Welcome to IUBAT QA Platform"
    body = (
        f"Hello {username},\n\n"
        "Thank you for joining IUBAT QA Platform. Your account has been created successfully.\n\n"
        "If you have any questions, please contact support.\n\n"
        "Best regards,\n"
        "IUBAT QA Platform Team"
    )
    _send_email(subject, body, email_address)
    return {"status": "queued", "email": email_address}


@celery.task(name="tasks.process_verification_request")
def process_verification_request(user_id: int, verification_id: int) -> dict[str, Any]:
    logger.info(
        "Processing verification request asynchronously: user_id=%s verification_id=%s",
        user_id,
        verification_id,
    )
    # Placeholder for long-running verification workflows.
    # This can be extended to upload the image to a secure service,
    # invoke AI moderation, or notify an admin pipeline.
    return {"user_id": user_id, "verification_id": verification_id, "status": "queued"}


@celery.task(name="tasks.publish_activity_event")
def publish_activity_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    logger.info("Activity event queued: %s %s", event_name, payload)
    return {"event": event_name, "payload": payload}
