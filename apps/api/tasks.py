"""
Celery tasks for the orchestration runtime (Phase 2.0).

Each task runs its own async engine (workers are sync processes); the shared
runtime logic lives in services/orchestration_runtime.py.
"""
import asyncio
import logging
import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from celery_app import celery_app

logger = logging.getLogger(__name__)

WORKER_URL = os.environ.get(
    "AFRIGROUND_WORKER_URL",
    "postgresql+asyncpg://afriground:afriground_dev_password@localhost:5433/afriground",
)


def _run_async(coro_factory):
    async def _runner():
        engine = create_async_engine(WORKER_URL, pool_pre_ping=True)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            return await coro_factory(factory)
        finally:
            await engine.dispose()

    return asyncio.run(_runner())


@celery_app.task(name="orchestration.drain_outbox", bind=True)
def drain_outbox(self, limit: int = 50) -> dict:
    """Publish due outbox events, then drive the simulated edge lifecycle."""
    from services.orchestration_runtime import drain, process_observation_events

    async def _run(factory):
        stats = await drain(factory, limit=limit)
        async with factory() as db:
            stats["simulated_transitions"] = await process_observation_events(db)
        return stats

    return _run_async(_run)


@celery_app.task(name="orchestration.metrics")
def outbox_metrics() -> dict:
    """Snapshot of outbox health for alerting / dashboards."""
    from services.orchestration_runtime import metrics

    async def _run(factory):
        async with factory() as db:
            return await metrics(db)

    return _run_async(_run)