"""
Shared environment loading for CLI scripts.

Credentials are never embedded in code: the gitignored repo-root `.env` is
loaded when present (mirrors apps/api/config.py), and callers fall back to the
`DATABASE_URL` env var or a passwordless localhost URL.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def database_url(specific_var: str | None = None, *, default_db: str = "afriground") -> str:
    return (
        os.environ.get(specific_var)
        if specific_var
        else None
    ) or os.environ.get("DATABASE_URL") or f"postgresql+asyncpg://localhost:5433/{default_db}"