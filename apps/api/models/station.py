from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from database import Base
import uuid

class GroundStation(Base):
    __tablename__ = 'ground_stations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    name_zh = Column(String(255))
    code = Column(String(50), unique=True, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_m = Column(Float, nullable=False)
    antenna_diameter_m = Column(Float)
    supported_bands = Column(JSONB)
    min_elevation_deg = Column(Float, default=5.0)
    status = Column(String(50), default='operational')
    country = Column(String(100), nullable=False)
    station_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MaintenanceEvent(Base):
    __tablename__ = 'maintenance_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    type = Column(String(50)) # planned, emergency, recurring
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    operational_impact = Column(String(255))
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Incident(Base):
    __tablename__ = 'incidents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    severity = Column(String(50))
    status = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
