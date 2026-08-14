from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class CompatibilityResult(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    PARTIALLY_COMPATIBLE = "PARTIALLY_COMPATIBLE"
    NOT_COMPATIBLE = "NOT_COMPATIBLE"

class SatelliteRFRequest(BaseModel):
    frequency: float # in MHz
    modulation: str
    symbol_rate: float
    polarization: str

class GroundStationCapabilities(BaseModel):
    supported_bands: List[dict] # e.g. [{"band": "S", "min_freq": 2000, "max_freq": 2300, "polarizations": ["RHCP", "LHCP"]}]
    supported_modulations: List[str]
    max_symbol_rate: float

class MatcherResult(BaseModel):
    status: CompatibilityResult
    reasons: List[str]

class CompatibilityEngine:
    """
    Evaluates if a Satellite's RF configuration can be serviced by a specific Ground Station.
    """
    
    def evaluate(self, sat_rf: SatelliteRFRequest, station_caps: GroundStationCapabilities) -> MatcherResult:
        reasons = []
        is_compatible = True
        is_partial = False

        # 1. Frequency Band Match
        freq_matched = False
        for band in station_caps.supported_bands:
            if band.get("min_freq", 0) <= sat_rf.frequency <= band.get("max_freq", float('inf')):
                freq_matched = True
                # Check polarization within that band
                if sat_rf.polarization not in band.get("polarizations", []):
                    reasons.append(f"Polarization '{sat_rf.polarization}' not supported in matching frequency band.")
                    is_compatible = False
                break
                
        if not freq_matched:
            reasons.append(f"Frequency {sat_rf.frequency} MHz not supported by any station band.")
            is_compatible = False

        # 2. Modulation Match
        if sat_rf.modulation not in station_caps.supported_modulations:
            reasons.append(f"Modulation '{sat_rf.modulation}' not supported.")
            is_compatible = False

        # 3. Symbol Rate Match
        if sat_rf.symbol_rate > station_caps.max_symbol_rate:
            reasons.append(f"Symbol rate {sat_rf.symbol_rate} exceeds station max {station_caps.max_symbol_rate}.")
            is_compatible = False
            
        if not is_compatible:
            # If all checks failed, we return NOT_COMPATIBLE. If some passed, it could be PARTIALLY_COMPATIBLE.
            # For simplicity, any hard requirement failure means NOT_COMPATIBLE in RF physics.
            # But let's assume if frequency matched but polarization didn't, it's partially compatible (maybe software defined).
            if freq_matched and len(reasons) == 1 and "Polarization" in reasons[0]:
                return MatcherResult(status=CompatibilityResult.PARTIALLY_COMPATIBLE, reasons=reasons)
                
            return MatcherResult(status=CompatibilityResult.NOT_COMPATIBLE, reasons=reasons)

        return MatcherResult(status=CompatibilityResult.COMPATIBLE, reasons=["Full RF match."])
