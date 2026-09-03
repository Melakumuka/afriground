from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from local_db import get_db, FirewallAuditLog, LCBEngagementLog, CRTRedundancyLog

router = APIRouter()

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(os.path.dirname(current_dir), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/local/audit", response_class=HTMLResponse)
async def audit_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Local-first audit log of firewall posture, LCB engagement, and CRT redundancy events."""
    firewall_result = await db.execute(
        select(FirewallAuditLog).order_by(FirewallAuditLog.ts.desc()).limit(100)
    )
    firewall_logs = firewall_result.scalars().all()

    lcb_result = await db.execute(
        select(LCBEngagementLog).order_by(LCBEngagementLog.ts.desc()).limit(100)
    )
    lcb_logs = lcb_result.scalars().all()

    crt_result = await db.execute(
        select(CRTRedundancyLog).order_by(CRTRedundancyLog.ts.desc()).limit(100)
    )
    crt_logs = crt_result.scalars().all()

    return templates.TemplateResponse("audit.html", {
        "request": request,
        "firewall_logs": firewall_logs,
        "lcb_logs": lcb_logs,
        "crt_logs": crt_logs,
    })
