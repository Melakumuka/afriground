"""
Publish hooks for the transactional outbox — concrete consumers registered
against event-type prefixes. See services/outbox.py::register_publish_hook.
"""
import logging
import os
import urllib.request
from typing import Optional

from services.outbox import OutboxEvent, register_publish_hook

logger = logging.getLogger(__name__)

WEBHOOK_URL = os.environ.get("AFRIGROUND_OUTBOX_WEBHOOK_URL")
WEBHOOK_TIMEOUT_S = float(os.environ.get("AFRIGROUND_OUTBOX_WEBHOOK_TIMEOUT", "5"))


@register_publish_hook("OBSERVATION_JOB.")
def dispatch_job_to_webhook(event: OutboxEvent) -> bool:
    """Forward observation job events to a configured webhook endpoint."""
    return _post_webhook(event)


@register_publish_hook("EXECUTION_RECEIPT.")
def dispatch_receipt_to_webhook(event: OutboxEvent) -> bool:
    return _post_webhook(event)


@register_publish_hook("STATION.")
def dispatch_station_to_webhook(event: OutboxEvent) -> bool:
    return _post_webhook(event)


def _post_webhook(event: OutboxEvent) -> bool:
    if not WEBHOOK_URL:
        logger.info("outbox event %s (%s) has no webhook configured; marked published", event.id, event.event_type)
        return True

    body = (
        '{"event_type":"%s","aggregate_type":"%s","aggregate_id":"%s","payload":%s}'
        % (
            event.event_type,
            event.aggregate_type,
            event.aggregate_id,
            _json_dumps(event.payload or {}),
        )
    ).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=WEBHOOK_TIMEOUT_S) as resp:
            ok = 200 <= resp.status < 300
            if not ok:
                logger.warning("webhook returned HTTP %s for event %s", resp.status, event.id)
            return ok
    except Exception as exc:  # noqa: BLE001
        logger.exception("webhook delivery failed for event %s: %s", event.id, exc)
        return False


def _json_dumps(obj) -> str:
    import json

    def _default(o):
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return str(o)

    return json.dumps(obj, default=_default)