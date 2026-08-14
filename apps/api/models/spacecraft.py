from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import Base
import uuid

class Satellite(Base):
    __tablename__ = 'satellites'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    norad_id = Column(Integer, unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TLESet(Base):
    __tablename__ = 'tle_sets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('satellites.id'), nullable=False)
    line1 = Column(String(69), nullable=False)
    line2 = Column(String(69), nullable=False)
    epoch = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SatelliteRFConfig(Base):
    __tablename__ = 'satellite_rf_configs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('satellites.id'), nullable=False)
    frequency = Column(Float)
    modulation = Column(String(100))
    symbol_rate = Column(Float)
    polarization = Column(String(50))
    protocol = Column(String(100))

class Constellation(Base):
    __tablename__ = 'constellations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

class ConstellationSatellite(Base):
    __tablename__ = 'constellation_satellites'
    
    constellation_id = Column(UUID(as_uuid=True), ForeignKey('constellations.id'), primary_key=True)
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('satellites.id'), primary_key=True)
    role = Column(String(100))

class ConstellationTasking(Base):
    __tablename__ = 'constellation_tasking'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    constellation_id = Column(UUID(as_uuid=True), ForeignKey('constellations.id'), nullable=False)
    task_type = Column(String(100))
    priority = Column(Integer)
    status = Column(String(50))
