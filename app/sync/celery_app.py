"""Celery application and beat schedule."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "canvas_wechat",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",  # Beijing time for quiet-hours logic
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)

# Celery Beat schedule
celery_app.conf.beat_schedule = {
    "sync-announcements": {
        "task": "app.sync.tasks.sync_announcements",
        "schedule": crontab(minute="*/5"),  # every 5 minutes
    },
    "sync-assignments": {
        "task": "app.sync.tasks.sync_assignments",
        "schedule": crontab(minute="*/15"),  # every 15 minutes
    },
    "sync-grades": {
        "task": "app.sync.tasks.sync_grades",
        "schedule": crontab(minute="0", hour="*"),  # every hour
    },
    "sync-enrollments": {
        "task": "app.sync.tasks.sync_enrollments",
        "schedule": crontab(minute="0", hour="*/6"),  # every 6 hours
    },
    "notification-check": {
        "task": "app.notifications.tasks.run_notification_check",
        "schedule": crontab(minute="0", hour="9,11,13,15,17,19,21"),  # active hours
    },
}

# Import task modules so Celery registers them
celery_app.autodiscover_tasks(
    ["app.sync.tasks", "app.notifications.tasks"],
    force=True,
)
