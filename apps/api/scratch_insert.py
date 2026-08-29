import asyncio
import uuid
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.abspath('c:/Users/melam/Documents/dev/gsas/afriGround/apps/api'))

from models.contact import ObservationJob, ExecutionReceipt, StationReadinessEvent
from auth import get_db_session

async def insert():
    async for db in get_db_session():
        org_id = uuid.UUID("ad205d66-3d1e-4f5f-8ce3-23f43fb88c51")
        job_id = uuid.uuid4()
        now = datetime.utcnow()
        
        job = ObservationJob(
            id=job_id,
            org_id=org_id,
            scheduled_contact_id=uuid.uuid4(),
            mission_profile_id=uuid.uuid4(),
            status="COMPLETED",
            priority=5,
            tx_requested=True,
            started_at=now - timedelta(minutes=10),
            completed_at=now
        )
        db.add(job)
        
        readiness = StationReadinessEvent(
            id=uuid.uuid4(),
            job_id=job_id,
            status="READY",
            confirmed_at=now - timedelta(minutes=15),
            checklist_results={"MCS Profile Loaded": True, "RF Path Verified": True, "Weather Safe": True},
            notes="Ready for pass"
        )
        db.add(readiness)
        
        receipt = ExecutionReceipt(
            id=uuid.uuid4(),
            observation_job_id=job_id,
            status="COMPLETED",
            carrier_locked=True,
            symbol_locked=True,
            received_bytes=500000000,
            average_ebno=12.5,
            pass_report_hash="abcdef1234567890",
            received_at=now
        )
        db.add(receipt)
        
        await db.commit()
        print(f"Inserted job {job_id}")

if __name__ == '__main__':
    asyncio.run(insert())
