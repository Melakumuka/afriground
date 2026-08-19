"""
Edge Agent mTLS Identity (Phase 4.0) — resolves a client certificate to a
StationAgentIdentity.

Deployment model: a TLS-terminating reverse proxy (nginx/traefik) requires
client certificates signed by the AfriGround CA, then injects the certificate
common name (== agent_id) via the configured header (default
`X-Client-Cert-CN`). The API never sees raw TLS, so the header is the identity
boundary and MUST only be injectable by the proxy. `agent_mtls_header_trusted`
is the kill-switch for non-proxy environments (defaults to True for local dev
and tests; set False in production to enforce TLS at the API itself).
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from config import settings
from models.station import GroundStation
from models.station_twin import StationAgentIdentity

logger = logging.getLogger(__name__)


@dataclass
class AgentIdentity:
    agent: StationAgentIdentity
    station: GroundStation


async def get_agent_identity(
    db: AsyncSession = Depends(get_db_session),
    x_client_cert_cn: Optional[str] = Header(None),
) -> AgentIdentity:
    """Resolve the mTLS client certificate CN to an active agent identity."""
    if not settings.agent_mtls_header_trusted:
        raise HTTPException(status_code=503, detail="Agent identity header disabled")
    if not x_client_cert_cn:
        raise HTTPException(
            status_code=401,
            detail=f"Missing {settings.agent_mtls_header} header (mTLS client certificate CN)",
        )

    agent = (
        await db.execute(
            select(StationAgentIdentity).where(
                StationAgentIdentity.agent_id == x_client_cert_cn
            )
        )
    ).scalars().first()
    if not agent:
        raise HTTPException(status_code=401, detail="Unknown agent identity")
    if agent.status != "active":
        raise HTTPException(status_code=401, detail="Agent identity is not active")

    now = datetime.now(timezone.utc)
    if agent.revoked_at and agent.revoked_at <= now:
        raise HTTPException(status_code=401, detail="Agent certificate revoked")
    if agent.certificate_valid_until and agent.certificate_valid_until <= now:
        raise HTTPException(status_code=401, detail="Agent certificate expired")

    station = await db.get(GroundStation, agent.station_id)
    if not station:
        raise HTTPException(status_code=401, detail="Agent station not found")

    return AgentIdentity(agent=agent, station=station)