from database import Base

# Import all models here so Alembic can discover them
from models.core import Role, Organization, User, Contract, Quote
from models.tenancy import Permission, RolePermission, AuditLog
from models.spacecraft import Satellite, TLESet, SatelliteRFConfig, Constellation, ConstellationSatellite, ConstellationTasking
from models.mission import (
    Spacecraft, Mission, MissionProfile, MissionRFProfile,
    MissionTelemetryDefinition, MissionTelecommandDefinition,
    MissionOperationalConstraint, MissionSLA,
)
from models.station import GroundStation, MaintenanceEvent, Incident
from models.station_twin import (
    StationCapability, StationHardware, StationLicense, StationCertification,
    StationCertificationEvent, StationQualityScore, StationTimeStatus, StationAgentIdentity,
)
from models.scheduling import PassPrediction, RecurringMission, Booking, Schedule, Operation
from models.contact import (
    VisibilityOpportunity, ContactOpportunity, Reservation, ScheduledContact,
    ObservationJob, ExecutionReceipt,
)
from models.events import JobEvent, OutboxEvent
from models.data import Dataset, DataDeliveryDestination, DataDeliveryJob, APIKey, Webhook, SupportTicket

# This ensures all models are registered with Base.metadata
__all__ = [
    "Base",
    "Role", "Organization", "User", "Contract", "Quote",
    "Permission", "RolePermission", "AuditLog",
    "Satellite", "TLESet", "SatelliteRFConfig", "Constellation", "ConstellationSatellite", "ConstellationTasking",
    "Spacecraft", "Mission", "MissionProfile", "MissionRFProfile",
    "MissionTelemetryDefinition", "MissionTelecommandDefinition",
    "MissionOperationalConstraint", "MissionSLA",
    "GroundStation", "MaintenanceEvent", "Incident",
    "StationCapability", "StationHardware", "StationLicense", "StationCertification",
    "StationCertificationEvent", "StationQualityScore", "StationTimeStatus", "StationAgentIdentity",
    "PassPrediction", "RecurringMission", "Booking", "Schedule", "Operation",
    "VisibilityOpportunity", "ContactOpportunity", "Reservation", "ScheduledContact",
    "ObservationJob", "ExecutionReceipt",
    "JobEvent", "OutboxEvent",
    "Dataset", "DataDeliveryDestination", "DataDeliveryJob", "APIKey", "Webhook", "SupportTicket"
]