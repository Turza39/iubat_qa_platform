import ssl
from celery import Celery
from config import settings


def _ssl_enabled():
    return settings.REDIS_SSL or settings.CELERY_BROKER_URL.startswith("rediss://")


celery = Celery(
    "iubat_qa_backend",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["utils.tasks"],  # Auto-discover tasks
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone=settings.TIMEZONE,
    enable_utc=True,

    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)

if _ssl_enabled():
    celery.conf.broker_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_NONE
    }
    celery.conf.redis_backend_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_NONE
    }