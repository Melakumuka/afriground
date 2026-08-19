"""
Orchestration runtime dispatcher — polls the outbox, publishes due events, and
(in simulate mode) drives the observation job lifecycle. Single implementation
shared with the Celery beat task (tasks.py::drain_outbox).

Run from apps/api:
    $env:AFRIGROUND_WORKER_URL="postgresql+asyncpg://afriground:afriground_dev_password@localhost:5433/afriground"
    & .venv\Scripts\python.exe scripts\outbox_worker.py --poll-interval 2
"""
import argparse
import asyncio
import logging
import os
import signal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import services.hooks  # noqa: F401  (registers publish hooks)
from services.orchestration_runtime import drain, process_observation_events

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("outbox_worker")

URL = os.environ.get(
    "AFRIGROUND_WORKER_URL",
    "postgresql+asyncpg://afriground:afriground_dev_password@localhost:5433/afriground",
)

_stop = asyncio.Event()


def _request_stop(signame: str) -> None:
    logger.info("received %s, draining...", signame)
    _stop.set()


async def drain_once(session_factory, limit: int) -> int:
    stats = await drain(session_factory, limit=limit)
    return stats["published"]


async def run(poll_interval: float, limit: int) -> None:
    engine = create_async_engine(URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        # fail fast if the DB is unreachable / not migrated
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1 FROM outbox_events LIMIT 0"))

        while not _stop.is_set():
            stats = await drain(session_factory, limit)
            if stats["published"]:
                logger.info("published %d outbox event(s)", stats["published"])
            async with session_factory() as db:
                applied = await process_observation_events(db)
            if applied:
                logger.info("simulated %d job transition(s)", applied)
            try:
                await asyncio.wait_for(_stop.wait(), timeout=poll_interval)
            except asyncio.TimeoutError:
                pass
    finally:
        await engine.dispose()
    logger.info("outbox worker stopped")


def main() -> None:
    parser = argparse.ArgumentParser(description="AfriGround outbox dispatcher")
    parser.add_argument("--poll-interval", type=float, default=5.0)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_event_loop().add_signal_handler(sig, _request_stop, sig.name)
        except NotImplementedError:
            pass  # Windows: no add_signal_handler

    asyncio.run(run(args.poll_interval, args.limit))


if __name__ == "__main__":
    main()