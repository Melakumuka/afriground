import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.scheduling import PassPrediction, Booking, Schedule
from models.station import GroundStation
from models.spacecraft import Satellite, SatelliteRFConfig
from services.matcher import CompatibilityEngine, SatelliteRFRequest, GroundStationCapabilities
from fastapi import HTTPException

class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.matcher = CompatibilityEngine()

    async def create_booking_request(self, org_id: uuid.UUID, satellite_id: uuid.UUID, pass_prediction_id: uuid.UUID) -> Booking:
        """
        Transition a Pass Prediction into a REQUESTED Booking.
        Also runs compatibility check before allowing the request.
        """
        # Fetch required data
        pass_pred = await self.db.get(PassPrediction, pass_prediction_id)
        if not pass_pred:
            raise HTTPException(status_code=404, detail="Pass prediction not found")
            
        station = await self.db.get(GroundStation, pass_pred.station_id)
        
        # In a real app we'd fetch the actual RF config for the satellite
        # For MVP we'll construct mock requests
        sat_rf = SatelliteRFRequest(
            frequency=2200.0, 
            modulation="QPSK", 
            symbol_rate=10.0, 
            polarization="RHCP"
        )
        
        station_caps = GroundStationCapabilities(
            supported_bands=station.supported_bands or [],
            supported_modulations=["QPSK", "BPSK"],
            max_symbol_rate=500.0
        )
        
        # Evaluate compatibility
        match_result = self.matcher.evaluate(sat_rf, station_caps)
        if match_result.status == "NOT_COMPATIBLE":
            raise HTTPException(status_code=400, detail=f"Satellite and Station are not compatible. Reasons: {', '.join(match_result.reasons)}")
            
        # Create Booking
        booking = Booking(
            org_id=org_id,
            satellite_id=satellite_id,
            status="REQUESTED"
        )
        self.db.add(booking)
        await self.db.flush() # get ID
        
        # Link prediction to booking, but we don't create a Schedule until it's confirmed
        # Actually in our schema, Schedule links Booking to PassPrediction. Let's create a DRAFT Schedule.
        schedule = Schedule(
            booking_id=booking.id,
            pass_prediction_id=pass_prediction_id,
            station_id=station.id,
            status="DRAFT" # Using DRAFT for schedules tied to unconfirmed bookings
        )
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(booking)
        
        return booking

    async def confirm_booking(self, booking_id: uuid.UUID) -> Booking:
        """
        Transition a Booking to CONFIRMED and its Schedule to SCHEDULED.
        """
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
            
        if booking.status != "REQUESTED" and booking.status != "RESERVED":
            raise HTTPException(status_code=400, detail=f"Cannot confirm booking in status {booking.status}")
            
        booking.status = "CONFIRMED"
        
        # Update related schedule
        stmt = select(Schedule).where(Schedule.booking_id == booking_id)
        result = await self.db.execute(stmt)
        schedule = result.scalar_one_or_none()
        
        if schedule:
            schedule.status = "SCHEDULED"
            
        await self.db.commit()
        await self.db.refresh(booking)
        
        # Here we would trigger the 'booking.confirmed' webhook
        return booking
