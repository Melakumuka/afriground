"""
Phase 3.1 tests — per-org webhook fan-out with HMAC signatures.
"""
import hashlib
import hmac
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from sqlalchemy import select

from models.data import Webhook, WebhookDelivery
from models.events import OutboxEvent
from services.outbox import emit, publish_pending
from services.webhooks import _signature, deliver_org_webhooks


class _CaptureHandler(BaseHTTPRequestHandler):
    captured = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        type(self).captured.append(
            {
                "path": self.path,
                "headers": {k.lower(): v for k, v in self.headers.items()},
                "body": body,
            }
        )
        if "/down" in self.path:
            self.send_response(404)
        else:
            self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


class _CaptureServer:
    def __init__(self):
        self.server = HTTPServer(("127.0.0.1", 0), _CaptureHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server.server_port}/hooks"

    def __enter__(self):
        _CaptureHandler.captured = []
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


async def _published_event(session, org_id, event_type="OBSERVATION_JOB.COMPLETED"):
    emit(
        session,
        aggregate_type="observation_job",
        aggregate_id=org_id,
        event_type=event_type,
        payload={"org_id": str(org_id), "job_id": str(org_id)},
    )
    await session.commit()
    published = await publish_pending(session, limit=50)
    assert published == 1
    return (
        await session.execute(
            select(OutboxEvent).where(OutboxEvent.event_type == event_type)
        )
    ).scalars().first()


async def _add_webhook(session, org_id, events, url):
    webhook = Webhook(
        org_id=org_id,
        url=url,
        secret="test-secret",
        events=events,
        is_active=True,
    )
    session.add(webhook)
    await session.flush()
    await session.commit()
    return webhook


async def test_fan_out_delivers_signed_payload(session, tenant):
    with _CaptureServer() as srv:
        webhook = await _add_webhook(session, tenant.org_id, ["OBSERVATION_JOB."], srv.url)
        event = await _published_event(session, tenant.org_id)

        stats = await deliver_org_webhooks(session)
        assert stats == {"delivered": 1, "failed": 0}

        captured = _CaptureHandler.captured
        assert len(captured) == 1
        body = captured[0]["body"]
        parsed = json.loads(body)
        assert parsed["event_type"] == "OBSERVATION_JOB.COMPLETED"
        assert parsed["payload"]["org_id"] == str(tenant.org_id)

        sig = captured[0]["headers"].get("x-afrground-signature", "")
        assert sig == _signature(webhook.secret, body)

        deliveries = (
            await session.execute(select(WebhookDelivery))
        ).scalars().all()
        assert len(deliveries) == 1
        assert deliveries[0].status == "delivered"
        assert deliveries[0].response_code == 200


async def test_fan_out_is_idempotent(session, tenant):
    with _CaptureServer() as srv:
        await _add_webhook(session, tenant.org_id, ["OBSERVATION_JOB."], srv.url)
        await _published_event(session, tenant.org_id)

        first = await deliver_org_webhooks(session)
        second = await deliver_org_webhooks(session)

        assert first["delivered"] == 1
        assert second == {"delivered": 0, "failed": 0}
        assert len(_CaptureHandler.captured) == 1


async def test_fan_out_skips_non_matching_event_types(session, tenant):
    with _CaptureServer() as srv:
        await _add_webhook(session, tenant.org_id, ["DATA_DELIVERY."], srv.url)
        await _published_event(session, tenant.org_id, event_type="STATION.REGISTERED")

        stats = await deliver_org_webhooks(session)
        assert stats == {"delivered": 0, "failed": 0}
        assert _CaptureHandler.captured == []


async def test_fan_out_tracks_failures(session, tenant):
    with _CaptureServer() as srv:
        await _add_webhook(session, tenant.org_id, ["OBSERVATION_JOB."], srv.url + "/down")
        await _published_event(session, tenant.org_id)

        stats = await deliver_org_webhooks(session)
        assert stats["failed"] == 1

        deliveries = (
            await session.execute(select(WebhookDelivery))
        ).scalars().all()
        assert len(deliveries) == 1
        assert deliveries[0].status == "failed"