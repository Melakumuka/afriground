from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import Base
import uuid

class JobEvent(Base):
    """State transition history for observation jobs (idempotent audit)."""
    __tablename__ = 'job_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    observation_job_id = Column(UUID(as_uuid=True), ForeignKey('observation_jobs.id'), nullable=False)
    from_state = Column(String(50))
    to_state = Column(String(50), nullable=False)
    actor = Column(String(255))
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OutboxEvent(Base):
    """Transactional outbox: durable events emitted with their owning transaction."""
    __tablename__ = 'outbox_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_type = Column(String(100), nullable=False)
    aggregate_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB)
    status = Column(String(50), default='PENDING', nullable=False)  # PENDING, PUBLISHED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True))