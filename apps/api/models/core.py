from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import Base
import uuid

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    # Examples: Platform Super Admin, GS Provider, GS Operator, Cust Admin, Mission Mgr, Data Analyst, Finance Mgr
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Organization(Base):
    __tablename__ = 'organizations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    country = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True) # from Supabase Auth
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'))
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'))
    preferred_language = Column(String(5), default='en')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Contract(Base):
    __tablename__ = 'contracts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    reserved_capacity_minutes = Column(Integer)
    sla_availability_target = Column(Float)
    status = Column(String(50)) # active, expired, pending

class Quote(Base):
    __tablename__ = 'quotes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    total_amount = Column(Float)
    status = Column(String(50)) # draft, sent, accepted, rejected
