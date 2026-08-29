"""
API Routes — Data Catalog & Delivery Engine
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import AsyncSessionLocal
from services.data_engine import (
    DataEngine,
    DatasetResponse,
    DeliveryDestinationRequest,
    DeliveryDestinationResponse,
    DeliveryJobResponse,
)

router = APIRouter(prefix="/api/v1/data", tags=["Data Engine"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Datasets ─────────────────────────────────────────────────────────────────

@router.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    product_type: Optional[str] = Query(None),
    max_cloud_cover: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = DataEngine(db)
    return await engine.list_datasets(product_type, max_cloud_cover)


# ── Delivery Destinations ────────────────────────────────────────────────────

@router.get("/destinations", response_model=List[DeliveryDestinationResponse])
async def list_destinations(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = DataEngine(db)
    org_id = uuid.UUID(user.get("org_id", "00000000-0000-0000-0000-000000000000"))
    return await engine.list_destinations(org_id)

@router.post("/destinations", response_model=DeliveryDestinationResponse)
async def add_destination(
    req: DeliveryDestinationRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = DataEngine(db)
    return await engine.add_destination(req)


# ── Delivery Jobs ────────────────────────────────────────────────────────────

@router.post("/delivery/{dataset_id}/to/{destination_id}", response_model=DeliveryJobResponse)
async def trigger_delivery(
    dataset_id: uuid.UUID,
    destination_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = DataEngine(db)
    return await engine.trigger_delivery(dataset_id, destination_id)


# ── Dataset Download (Fallback) ──────────────────────────────────────────────

@router.get("/datasets/{job_id}/download")
async def download_dataset(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Generate a pre-signed GET URL for downloading raw IQ data from AfriGround MinIO.
    If the data was directly routed to the customer's cloud, this returns 404 since
    AfriGround does not hold the data or read credentials.
    """
    from models.data import Dataset
    from services.storage import StorageService
    from config import settings
    from sqlalchemy import select
    from fastapi import HTTPException

    # 1. Ensure user owns the job (we could check org_id on ObservationJob, but Dataset links to it)
    from models.contact import ObservationJob
    job = await db.get(ObservationJob, job_id)
    org_id = uuid.UUID(user.get("org_id", "00000000-0000-0000-0000-000000000000"))
    
    if not job or job.org_id != org_id:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # 2. Get dataset
    stmt = select(Dataset).where(Dataset.observation_job_id == job_id)
    res = await db.execute(stmt)
    dataset = res.scalars().first()

    if not dataset or not dataset.storage_url:
        raise HTTPException(status_code=404, detail="Data not available")

    # 3. Check if it's AfriGround MinIO or Customer Cloud
    # Storage URL format for internal MinIO: minio://afriground-raw/observations/{job.id}/raw.bin
    # or s3://afriground-raw-internal/...
    if not (dataset.storage_url.startswith("minio://afriground") or dataset.storage_url.startswith("s3://afriground")):
        raise HTTPException(
            status_code=404, 
            detail="Data was uploaded directly to your configured cloud destination. AfriGround does not hold a copy."
        )

    # 4. Generate pre-signed GET URL
    fallback_config = {
        "access_key": settings.s3_access_key,
        "secret_key": settings.s3_secret_key,
        "endpoint": settings.s3_endpoint_url,
        "bucket": "afriground-raw"
    }
    
    # We use a trick: `StorageService.generate_presigned_url` currently hardcodes 'put_object'.
    # We should use standard boto3 directly here for GET, or update StorageService. 
    # Updating standard boto3 for get_object is simpler here.
    import boto3
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )
    
    # Extract key from url
    # e.g., minio://afriground-raw/observations/123/raw.bin -> observations/123/raw.bin
    parts = dataset.storage_url.split("afriground-raw", 1)
    key = parts[1].lstrip("/") if len(parts) > 1 else f"artifacts/{job_id}/raw.bin"

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": "afriground-raw", "Key": key},
            ExpiresIn=3600,
        )
        return {"ok": True, "download_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not generate download URL")
