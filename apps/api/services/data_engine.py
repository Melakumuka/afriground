"""
Data Delivery Engine — Handles datasets, storage locations, and automated delivery jobs.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from pydantic import BaseModel

from models.data import Dataset, DataDeliveryDestination, DataDeliveryJob


# ── Schemas ──────────────────────────────────────────────────────────────────

class DatasetResponse(BaseModel):
    id: uuid.UUID
    schedule_id: Optional[uuid.UUID]
    satellite_id: Optional[uuid.UUID]
    sensor_type: Optional[str]
    cloud_cover: Optional[float]
    processing_level: Optional[str]
    product_type: Optional[str]
    acquisition_date: Optional[datetime]
    storage_url: Optional[str]

class DeliveryDestinationRequest(BaseModel):
    org_id: uuid.UUID
    type: str  # s3, gcs, webhook, api
    config: dict

class DeliveryDestinationResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    type: str
    is_active: bool

class DeliveryJobResponse(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    destination_id: uuid.UUID
    status: str
    created_at: datetime


# ── Service ──────────────────────────────────────────────────────────────────

class DataEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Dataset Catalog ──────────────────────────────────────────────────────

    async def list_datasets(
        self,
        product_type: Optional[str] = None,
        max_cloud_cover: Optional[float] = None,
    ) -> List[DatasetResponse]:
        """Query datasets, optionally filtering by product type or cloud cover."""
        stmt = select(Dataset)

        if product_type:
            stmt = stmt.where(Dataset.product_type == product_type)
        if max_cloud_cover is not None:
            stmt = stmt.where(Dataset.cloud_cover <= max_cloud_cover)

        stmt = stmt.order_by(Dataset.acquisition_date.desc())
        result = await self.db.execute(stmt)
        datasets = result.scalars().all()

        return [
            DatasetResponse(
                id=ds.id,
                schedule_id=ds.schedule_id,
                satellite_id=ds.satellite_id,
                sensor_type=ds.sensor_type,
                cloud_cover=ds.cloud_cover,
                processing_level=ds.processing_level,
                product_type=ds.product_type,
                acquisition_date=ds.acquisition_date,
                storage_url=ds.storage_url,
            )
            for ds in datasets
        ]

    # ── Delivery Destinations ────────────────────────────────────────────────

    async def add_destination(self, req: DeliveryDestinationRequest) -> DeliveryDestinationResponse:
        """Register a new customer delivery destination (S3, GCS, Webhook)."""
        if req.type not in ["s3", "gcs", "webhook", "api"]:
            raise HTTPException(status_code=400, detail="Invalid destination type")

        dest = DataDeliveryDestination(
            org_id=req.org_id,
            type=req.type,
            config=req.config,
            is_active=True,
        )
        self.db.add(dest)
        await self.db.commit()
        await self.db.refresh(dest)

        return DeliveryDestinationResponse(
            id=dest.id,
            org_id=dest.org_id,
            type=dest.type,
            is_active=dest.is_active,
        )

    # ── Delivery Jobs ────────────────────────────────────────────────────────

    async def trigger_delivery(self, dataset_id: uuid.UUID, destination_id: uuid.UUID) -> DeliveryJobResponse:
        """Queue a dataset for delivery to a specific destination."""
        dataset = await self.db.get(Dataset, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        dest = await self.db.get(DataDeliveryDestination, destination_id)
        if not dest:
            raise HTTPException(status_code=404, detail="Destination not found")

        job = DataDeliveryJob(
            dataset_id=dataset.id,
            destination_id=dest.id,
            status="pending",
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        # In a real environment, this would push a task to Celery/Redis
        # which would execute the actual S3/GCP copy or webhook push.

        return DeliveryJobResponse(
            id=job.id,
            dataset_id=job.dataset_id,
            destination_id=job.destination_id,
            status=job.status,
            created_at=job.created_at,
        )
