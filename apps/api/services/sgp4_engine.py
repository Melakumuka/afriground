import datetime
from typing import List, Optional, Tuple
from skyfield.api import Topos, EarthSatellite, load, wgs84
from pydantic import BaseModel

class PassResult(BaseModel):
    aos: datetime.datetime
    los: datetime.datetime
    max_elevation: float
    duration_seconds: int

class SGP4Engine:
    def __init__(self):
        # Load the timescale and ephemeris (this usually downloads de421.bsp on first run, 
        # but skyfield handles caching it). For production, we should package this or pre-download.
        self.ts = load.timescale()

    def _get_satellite(self, tle_line1: str, tle_line2: str, name: str = "Satellite") -> EarthSatellite:
        return EarthSatellite(tle_line1, tle_line2, name, self.ts)

    def _get_station(self, lat: float, lon: float, alt_m: float) -> Topos:
        # Using WGS84 for topocentric coordinates
        return wgs84.latlon(lat, lon, elevation_m=alt_m)

    def predict_passes(
        self,
        tle_line1: str,
        tle_line2: str,
        station_lat: float,
        station_lon: float,
        station_alt_m: float,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        min_elevation_deg: float = 5.0,
    ) -> List[PassResult]:
        """
        Predict satellite passes over a specific ground station within a time window.
        """
        satellite = self._get_satellite(tle_line1, tle_line2)
        station = self._get_station(station_lat, station_lon, station_alt_m)

        t0 = self.ts.from_datetime(start_time)
        t1 = self.ts.from_datetime(end_time)

        # find_events returns time objects and an array of event types (0: AOS, 1: Max El, 2: LOS)
        t_events, events = satellite.find_events(station, t0, t1, altitude_degrees=min_elevation_deg)
        
        passes = []
        current_aos = None
        current_max_el = None

        for t, event in zip(t_events, events):
            if event == 0: # AOS
                current_aos = t.utc_datetime()
                current_max_el = None
            elif event == 1: # Max elevation
                # Calculate the exact elevation at this time
                difference = satellite - station
                topocentric = difference.at(t)
                alt, az, distance = topocentric.altaz()
                current_max_el = alt.degrees
            elif event == 2: # LOS
                if current_aos:
                    los_time = t.utc_datetime()
                    duration = int((los_time - current_aos).total_seconds())
                    # In case max elevation event was missed or not calculated correctly
                    if current_max_el is None:
                        current_max_el = min_elevation_deg # fallback
                    
                    passes.append(PassResult(
                        aos=current_aos,
                        los=los_time,
                        max_elevation=round(current_max_el, 2),
                        duration_seconds=duration
                    ))
                current_aos = None
                current_max_el = None

        return passes
