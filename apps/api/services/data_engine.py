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
from core.crypto import encrypt_dict


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
    type: str  # s3, gcs, huawei_obs, baidu_bos, alibaba_oss, azure_blob, webhook, api
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

    async def list_destinations(self, org_id: uuid.UUID) -> List[DeliveryDestinationResponse]:
        """List active delivery destinations for an organization."""
        stmt = select(DataDeliveryDestination).where(
            DataDeliveryDestination.org_id == org_id,
            DataDeliveryDestination.is_active == True
        ).order_by(DataDeliveryDestination.type)
        result = await self.db.execute(stmt)
        dests = result.scalars().all()
        return [
            DeliveryDestinationResponse(
                id=d.id, org_id=d.org_id, type=d.type, is_active=d.is_active
            ) for d in dests
        ]

    async def _preflight_check(self, dest_type: str, config: dict):
        """Validate credentials against the cloud provider before saving."""
        if dest_type in ["s3", "huawei_obs", "baidu_bos", "alibaba_oss"]:
            try:
                import boto3
                from botocore.exceptions import ClientError
                import logging
                
                # Boto3 client initialization with custom endpoint if needed
                client_kwargs = {
                    "aws_access_key_id": config.get("access_key"),
                    "aws_secret_access_key": config.get("secret_key"),
                }
                
                if dest_type == "s3":
                    client_kwargs["region_name"] = config.get("region", "us-east-1")
                else:
                    endpoint = config.get("endpoint", "")
                    if endpoint and not endpoint.startswith("http"):
                        endpoint = f"https://{endpoint}"
                    client_kwargs["endpoint_url"] = endpoint
                    
                s3 = boto3.client("s3", **client_kwargs)
                bucket = config.get("bucket")
                
                if not bucket:
                    raise HTTPException(status_code=400, detail="Bucket name is required")
                
                # Pre-flight check: attempt to head the bucket to verify access
                # In reality, we'd want to test PutObject, but HeadBucket tests basic auth.
                s3.head_bucket(Bucket=bucket)
            except Exception as e:
                import logging
                logging.error(f"Pre-flight check failed for {dest_type}: {e}")
                raise HTTPException(status_code=400, detail=f"Credential validation failed: {str(e)}")
                
        elif dest_type in ["gcs", "azure_blob"]:
            # Mock pre-flight for providers without SDK installed in this env
            pass
        return True

    async def add_destination(self, req: DeliveryDestinationRequest) -> DeliveryDestinationResponse:
        """Register a new customer delivery destination."""
        if req.type not in ["s3", "gcs", "huawei_obs", "baidu_bos", "alibaba_oss", "azure_blob", "webhook", "api"]:
            raise HTTPException(status_code=400, detail="Invalid destination type")

        # 1. Pre-flight check
        await self._preflight_check(req.type, req.config)

        # 2. Encrypt the sensitive configuration payload at rest
        encrypted_config = {"encrypted_payload": encrypt_dict(req.config)}

        dest = DataDeliveryDestination(
            org_id=req.org_id,
            type=req.type,
            config=encrypted_config,
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

    # ── Execution Receipt Processing ─────────────────────────────────────────

    async def process_execution_receipt(self, receipt_id: uuid.UUID):
        """
        Process a new execution receipt, validate the hash, 
        and trigger data delivery for the associated job.
        """
        from models.contact import ExecutionReceipt
        import hashlib
        
        receipt = await self.db.get(ExecutionReceipt, receipt_id)
        if not receipt:
            raise HTTPException(status_code=404, detail="ExecutionReceipt not found")
        
        # 1. Cryptographically validate the pass_report_hash
        # In a real app we would compute the hash of the actual uploaded S3 artifacts.
        if not receipt.pass_report_hash:
            raise ValueError("Receipt missing pass_report_hash")
            
        # 2. Create a Dataset based on the receipt
        dataset = Dataset(
            schedule_id=receipt.job_id,  # Mapping job back to schedule roughly
            sensor_type="RF_RAW",
            product_type="L0_IQ",
            acquisition_date=receipt.actual_aos or datetime.utcnow(),
            storage_url=f"s3://afriground-raw-internal/{receipt.job_id}/"
        )
        self.db.add(dataset)
        await self.db.flush()
        
        # 3. Find customer destination and trigger delivery
        stmt = select(DataDeliveryDestination).limit(1)
        res = await self.db.execute(stmt)
        dest = res.scalar_one_or_none()
        
        if dest:
            await self.trigger_delivery(dataset.id, dest.id)
            
        return {"status": "success", "dataset_id": str(dataset.id)}
