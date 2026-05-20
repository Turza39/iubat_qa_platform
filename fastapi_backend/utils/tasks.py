import logging
from typing import Any

from .celery_app import celery
from .redis_cache import delete_pattern_sync

logger = logging.getLogger(__name__)


# =========================
# CACHE INVALIDATION TASK
# =========================
@celery.task(name="tasks.invalidate_cache_prefix")
def invalidate_cache_prefix(prefix: str) -> dict[str, Any]:
    try:
        deleted = delete_pattern_sync(f"{prefix}*")
        logger.info("Invalidated cache prefix %s (deleted %s keys)", prefix, deleted)
        return {"prefix": prefix, "deleted": deleted}
    except Exception as exc:
        logger.exception("Cache invalidation failed for prefix %s: %s", prefix, exc)
        return {"prefix": prefix, "deleted": 0, "error": str(exc)}


# =========================
# WELCOME EMAIL (DISABLED)
# =========================
@celery.task(name="tasks.send_welcome_email")
def send_welcome_email(email_address: str, username: str) -> dict[str, str]:
    logger.info(
        "Email feature disabled. Skipping welcome email for %s (%s)",
        username,
        email_address,
    )
    return {
        "status": "disabled",
        "email": email_address,
        "message": "Email service not enabled"
    }


# =========================
# VERIFICATION REQUEST
# =========================
@celery.task(name="tasks.process_verification_request")
def process_verification_request(user_id: int, verification_id: int) -> dict[str, Any]:
    logger.info(
        "Processing verification request asynchronously: user_id=%s verification_id=%s",
        user_id,
        verification_id,
    )

    # Placeholder for future pipeline (Supabase storage, AI moderation, etc.)
    return {
        "user_id": user_id,
        "verification_id": verification_id,
        "status": "queued"
    }


# =========================
# ACTIVITY EVENT PUBLISHER
# =========================
@celery.task(name="tasks.publish_activity_event")
def publish_activity_event(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    logger.info("Activity event queued: %s %s", event_name, payload)

    return {
        "event": event_name,
        "payload": payload
    }