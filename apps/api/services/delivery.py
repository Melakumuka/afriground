"""
Data Delivery Pipeline (Phase 2.3) — when an observation job completes, the
orchestration runtime materializes a dataset and executes delivery jobs to
every active customer destination, emitting DATA_DELIVERY.* outbox events.

Delivery execution is simulated (checksummed audit trail) — real S3/webhook
transfer is a Phase 2.3+ production concern.
"""
import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contact import ObservationJob, ScheduledContact
from models.data import DataDeliveryDestination, DataDeliveryJob, Dataset
from models.mission import Spacecraft
from services.outbox import emit

logger = logging.getLogger(__name__)

RETENTION_DAYS = 30


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _checksum(dataset_id: uuid.UUID, destination_id: uuid.UUID) -> str:
    digest = hashlib.sha256(f"{dataset_id}:{destination_id}".encode("utf-8")).hexdigest()
    return digest


class DeliveryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ensure_dataset_for_job(self, job: ObservationJob) -> Dataset:
        existing = (
            await self.db.execute(
                select(Dataset).where(Dataset.observation_job_id == job.id)
            )
        ).scalars().first()
        if existing:
            return existing

        satellite_id = None
        acquisition = _now()
        contact = await self.db.get(ScheduledContact, job.scheduled_contact_id)
        if contact:
            acquisition = contact.scheduled_start or _now()
            spacecraft = await self.db.get(Spacecraft, contact.spacecraft_id)
            if spacecraft:
                satellite_id = spacecraft.satellite_id

        dataset = Dataset(
            observation_job_id=job.id,
            satellite_id=satellite_id,
            sensor_type="rf",
            processing_level="L0",
            product_type="raw",
            acquisition_date=acquisition,
            storage_url=f"minio://afriground-raw/observations/{job.id}/raw.bin",
        )
        self.db.add(dataset)
        await self.db.flush()
        emit(
            self.db,
            aggregate_type="dataset",
            aggregate_id=dataset.id,
            event_type="DATA_DELIVERY.DATASET_READY",
            payload={"dataset_id": str(dataset.id), "observation_job_id": str(job.id)},
        )
        return dataset

    async def on_job_completed(self, job: ObservationJob) -> List[DataDeliveryJob]:
        """Materialize the dataset and execute delivery to every active destination.

        Returns the created delivery jobs. The caller owns the transaction.
        """
        dataset = await self.ensure_dataset_for_job(job)

        destinations = (
            await self.db.execute(
                select(DataDeliveryDestination).where(
                    DataDeliveryDestination.org_id == job.org_id,
                    DataDeliveryDestination.is_active == True,  # noqa: E712
                )
            )
        ).scalars().all()

        created: List[DataDeliveryJob] = []
        for i, dest in enumerate(destinations):
            existing = (
                await self.db.execute(
                    select(DataDeliveryJob).where(
                        DataDeliveryJob.dataset_id == dataset.id,
                        DataDeliveryJob.destination_id == dest.id,
                    )
                )
            ).scalars().first()
            if existing:
                created.append(existing)
                continue

            # Phase 8: Smart Routing. 
            # The Edge Agent already uploaded the artifact directly to the primary (first) destination.
            # We record it as delivered, but we skip emitting the "simulated delivery" event
            # to avoid any downstream double-delivery logic.
            is_primary_smart_route = (i == 0)

            job_row = DataDeliveryJob(
                dataset_id=dataset.id,
                destination_id=dest.id,
                status="processing",
            )
            self.db.add(job_row)
            await self.db.flush()
            job_row.status = "delivered"
            job_row.checksum = _checksum(dataset.id, dest.id)
            job_row.retention_expires_at = _now() + timedelta(days=RETENTION_DAYS)
            
            if not is_primary_smart_route:
                emit(
                    self.db,
                    aggregate_type="data_delivery",
                    aggregate_id=job_row.id,
                    event_type="DATA_DELIVERY.COMPLETED",
                    payload={
                        "delivery_job_id": str(job_row.id),
                        "dataset_id": str(dataset.id),
                        "destination_id": str(dest.id),
                        "checksum": job_row.checksum,
                        "org_id": str(job.org_id) if job.org_id else None,
                    },
                )
            created.append(job_row)

        if created:
            logger.info("delivery: %d delivery job(s) executed for job %s", len(created), job.id)
        return created

    async def list_delivery_jobs(self, org_id: uuid.UUID, limit: int = 50) -> List[DataDeliveryJob]:
        stmt = (
            select(DataDeliveryJob)
            .join(Dataset, Dataset.id == DataDeliveryJob.dataset_id)
            .join(ObservationJob, ObservationJob.id == Dataset.observation_job_id)
            .where(ObservationJob.org_id == org_id)
            .order_by(DataDeliveryJob.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())