import asyncio
import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from conftest import TEST_URL


def _alembic_config() -> Config:
    # env.py reads AFRIGROUND_ALEMBIC_URL first; make sure it targets the test DB.
    os.environ["AFRIGROUND_ALEMBIC_URL"] = TEST_URL
    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "alembic"))
    cfg.set_main_option("sqlalchemy.url", TEST_URL)
    return cfg


async def _run_upgrade_head():
    cfg = _alembic_config()
    await asyncio.to_thread(command.upgrade, cfg, "head")


@pytest.mark.asyncio
async def test_migration_applies_cleanly(engine, session):
    await _run_upgrade_head()

    async with engine.connect() as conn:
        version = (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalar()
        assert version is not None and len(version) >= 8

        table_count = (
            await conn.execute(
                text("SELECT count(*) FROM pg_tables WHERE schemaname = 'public'")
            )
        ).scalar()
        assert table_count >= 50  # full Phase 1 schema present


@pytest.mark.asyncio
async def test_migration_is_idempotent(engine, session):
    await _run_upgrade_head()  # already at head -> no-op, must not raise
    await _run_upgrade_head()  # run twice


@pytest.mark.asyncio
async def test_no_extension_schema_drops(engine, session):
    """Guard against the tiger/topology regression: the migration must never
    emit DROP TABLE for PostGIS extension schemas."""
    async with engine.connect() as conn:
        tiger_tables = (
            await conn.execute(
                text("SELECT count(*) FROM pg_tables WHERE schemaname = 'tiger'")
            )
        ).scalar()
        assert tiger_tables > 0  # extensions intact

        geo_cols = (
            await conn.execute(
                text(
                    "SELECT count(*) FROM information_schema.columns "
                    "WHERE table_schema='public' AND udt_name='geometry'"
                )
            )
        ).scalar()
        assert geo_cols >= 2  # ground_stations.location + datasets.aoi