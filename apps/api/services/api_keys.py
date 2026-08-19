"""
API Key Authentication (Phase 3.1) — programmatic access for platform/GS
operators. Keys are stored as SHA-256 hashes; the plaintext is shown once at
creation. Scope list + rate-limit tier are carried on the APIKey row.
"""
import hashlib
import secrets
import uuid
from typing import List, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from models.data import APIKey

KEY_PREFIX = "agk_"


def _hash_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def generate_api_key(
    db: AsyncSession,
    org_id: uuid.UUID,
    name: str = "default",
    scopes: Optional[List[str]] = None,
    tier: str = "standard",
) -> tuple[APIKey, str]:
    """Create a key and return (row, plaintext). Plaintext is shown once."""
    plaintext = KEY_PREFIX + secrets.token_hex(24)
    row = APIKey(
        org_id=org_id,
        name=name,
        key_hash=_hash_key(plaintext),
        scopes=scopes or [],
        rate_limit_tier=tier,
        is_active=True,
    )
    db.add(row)
    return row, plaintext


async def verify_api_key(db: AsyncSession, plaintext: str) -> Optional[APIKey]:
    """Resolve a presented key to its (active) row, or None."""
    if not plaintext.startswith(KEY_PREFIX):
        return None
    stmt = select(APIKey).where(
        APIKey.key_hash == _hash_key(plaintext),
        APIKey.is_active == True,  # noqa: E712
    )
    return (await db.execute(stmt)).scalars().first()


async def list_api_keys(db: AsyncSession, org_id: uuid.UUID) -> List[APIKey]:
    stmt = (
        select(APIKey)
        .where(APIKey.org_id == org_id)
        .order_by(APIKey.created_at.desc())
    )
    return list((await db.execute(stmt)).scalars().all())


async def revoke_api_key(db: AsyncSession, key_id: uuid.UUID, org_id: uuid.UUID) -> bool:
    row = await db.get(APIKey, key_id)
    if not row or row.org_id != org_id:
        return False
    row.is_active = False
    return True


async def get_api_key_context(
    db: AsyncSession = Depends(get_db_session),
    x_api_key: Optional[str] = Header(None),
) -> dict:
    """Dependency: authenticate a request via the X-API-Key header."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    row = await verify_api_key(db, x_api_key)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    return {"org_id": row.org_id, "key_id": row.id, "scopes": row.scopes or []}