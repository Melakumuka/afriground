from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import Base
import uuid

class PassPrediction(Base):
    __tablename__ = 'pass_predictions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('satellites.id'), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    aos = Column(DateTime(timezone=True), nullable=False)
    los = Column(DateTime(timezone=True), nullable=False)
    max_elevation = Column(Float, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RecurringMission(Base):
    __tablename__ = 'recurring_missions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('satellites.id'), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'))
    passes_per_day = Column(Integer)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String(50)) # active, paused, completed

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('satellites.id'), nullable=False)
    status = Column(String(50), nullable=False) # DRAFT, REQUESTED, QUOTED, RESERVED, CONFIRMED, CANCELLED, EXPIRED
    recurring_mission_id = Column(UUID(as_uuid=True), ForeignKey('recurring_missions.id'))
    quote_id = Column(UUID(as_uuid=True), ForeignKey('quotes.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Schedule(Base):
    __tablename__ = 'schedules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey('bookings.id'), nullable=False)
    pass_prediction_id = Column(UUID(as_uuid=True), ForeignKey('pass_predictions.id'), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    status = Column(String(50), nullable=False) # SCHEDULED, EXECUTING, COMPLETED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Operation(Base):
    __tablename__ = 'operations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('schedules.id'), nullable=False)
    actual_aos = Column(DateTime(timezone=True))
    actual_los = Column(DateTime(timezone=True))
    telemetry_log_url = Column(String(1024))
    failure_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
