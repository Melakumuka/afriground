"""
Celery application for the AfriGround orchestration runtime (Phase 2.0).

The outbox is the source of truth; Celery beat just schedules the drain. The
actual publishing + lifecycle processing is shared in
services/orchestration_runtime.py.

Run (from apps/api):
    & .venv\Scripts\celery.exe -A celery_app worker --beat -l info
"""
from celery import Celery

from config import settings

celery_app = Celery(
    "afriground",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    beat_schedule={
        "drain-outbox": {
            "task": "orchestration.drain_outbox",
            "schedule": settings.outbox_poll_interval,
        },
        "check-heartbeats": {
            "task": "orchestration.check_heartbeats",
            "schedule": settings.heartbeat_check_interval_s,
        },
        "sweep-recurring": {
            "task": "commercial.sweep_recurring",
            "schedule": settings.recurring_sweep_interval_s,
        },
    },
)