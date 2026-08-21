from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from local_db import get_db, CachedJob, CachedProfile
from cloud_client import CloudClient
from adapters import get_adapter
from config import settings
import os

router = APIRouter()

# Get the absolute path to the templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(os.path.dirname(current_dir), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    # Fetch health
    adapter = get_adapter(settings.adapter_type)
    health = await adapter.get_station_health()

    # Fetch upcoming jobs from local DB
    result = await db.execute(select(CachedJob).order_by(CachedJob.scheduled_start))
    jobs = result.scalars().all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "health": health,
        "jobs": jobs
    })

@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def pass_console(request: Request, job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(CachedJob, job_id)
    if not job:
        return HTMLResponse("Job not found", status_code=404)
        
    profile = None
    if job.station_operation_profile_id:
        profile = await db.get(CachedProfile, job.station_operation_profile_id)
        
    return templates.TemplateResponse("pass_console.html", {
        "request": request,
        "job": job,
        "profile": profile
    })

@router.post("/jobs/{job_id}/ready")
async def confirm_ready(
    job_id: str, 
    mcs_loaded: Optional[bool] = Form(False),
    weather_safe: Optional[bool] = Form(False),
    rf_verified: Optional[bool] = Form(False),
    db: AsyncSession = Depends(get_db)
):
    checklist_results = {
        "mcs_profile_loaded": mcs_loaded,
        "weather_safe": weather_safe,
        "rf_path_verified": rf_verified
    }
    
    client = CloudClient()
    await client.submit_readiness(job_id, status="READY", checklist_results=checklist_results)
    
    # Update local state
    job = await db.get(CachedJob, job_id)
    if job:
        job.readiness_status = "READY"
        await db.commit()
        
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)
