from database import Base

# Import all models here so Alembic can discover them
from models.core import Role, Organization, User, Contract, Quote
from models.spacecraft import Satellite, TLESet, SatelliteRFConfig, Constellation, ConstellationSatellite, ConstellationTasking
from models.station import GroundStation, MaintenanceEvent, Incident
from models.scheduling import PassPrediction, RecurringMission, Booking, Schedule, Operation
from models.data import Dataset, DataDeliveryDestination, DataDeliveryJob, APIKey, Webhook, SupportTicket

# This ensures all models are registered with Base.metadata
__all__ = [
    "Base",
    "Role", "Organization", "User", "Contract", "Quote",
    "Satellite", "TLESet", "SatelliteRFConfig", "Constellation", "ConstellationSatellite", "ConstellationTasking",
    "GroundStation", "MaintenanceEvent", "Incident",
    "PassPrediction", "RecurringMission", "Booking", "Schedule", "Operation",
    "Dataset", "DataDeliveryDestination", "DataDeliveryJob", "APIKey", "Webhook", "SupportTicket"
]
