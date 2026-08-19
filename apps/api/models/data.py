from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from database import Base
import uuid

class Dataset(Base):
    __tablename__ = 'datasets'
    __table_args__ = (
        Index('idx_datasets_aoi', 'aoi', postgresql_using='gist'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('schedules.id'))
    observation_job_id = Column(UUID(as_uuid=True), ForeignKey('observation_jobs.id'))
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('satellites.id'))
    sensor_type = Column(String(100))
    aoi = Column(Geometry('POLYGON', srid=4326, spatial_index=False))
    cloud_cover = Column(Float)
    processing_level = Column(String(50))
    product_type = Column(String(100))
    acquisition_date = Column(DateTime(timezone=True))
    storage_url = Column(String(1024))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DataDeliveryDestination(Base):
    __tablename__ = 'data_delivery_destinations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    type = Column(String(50)) # s3, gcs, webhook, api
    config = Column(JSONB)
    is_active = Column(Boolean, default=True)

class DataDeliveryJob(Base):
    __tablename__ = 'data_delivery_jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey('datasets.id'), nullable=False)
    destination_id = Column(UUID(as_uuid=True), ForeignKey('data_delivery_destinations.id'), nullable=False)
    status = Column(String(50)) # pending, processing, delivered, failed
    checksum = Column(String(255))
    retention_expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class APIKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255))
    key_hash = Column(String(255), nullable=False)
    scopes = Column(JSONB)
    rate_limit_tier = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Webhook(Base):
    __tablename__ = 'webhooks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    url = Column(String(1024), nullable=False)
    secret = Column(String(255), nullable=False)
    events = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    subject = Column(String(255), nullable=False)
    status = Column(String(50), default='open')
    priority = Column(String(50), default='normal')
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
