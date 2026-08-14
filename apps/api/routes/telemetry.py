"""
Real-time Telemetry WebSocket — Streams live pass execution data to the frontend.
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from hal import EdgeNodeFactory

router = APIRouter(tags=["Telemetry"])

# Track active WebSocket connections per schedule
active_connections: Dict[str, Set[WebSocket]] = {}

# Shared HAL factory (mock mode for development)
hal_factory = EdgeNodeFactory(mode="mock")


@router.websocket("/ws/telemetry/{schedule_id}")
async def telemetry_stream(websocket: WebSocket, schedule_id: str):
    """
    WebSocket endpoint that streams real-time telemetry during a pass execution.
    
    Sends JSON messages with antenna position, RF status, signal quality,
    weather, recording progress, and power status every second.
    """
    await websocket.accept()

    # Register connection
    if schedule_id not in active_connections:
        active_connections[schedule_id] = set()
    active_connections[schedule_id].add(websocket)

    # Get controller instances
    antenna = hal_factory.get_antenna_controller()
    rf = hal_factory.get_rf_controller()
    receiver = hal_factory.get_receiver_controller()
    weather = hal_factory.get_weather_controller()
    recording = hal_factory.get_recording_controller()
    power = hal_factory.get_power_controller()

    try:
        # Simulate pass execution startup
        await rf.set_frequency(2200.0)
        await rf.set_modulation("QPSK", 10.0)
        await receiver.start_receive(2200.0, "QPSK")
        await recording.start_recording(f"/data/recordings/{schedule_id}.raw")

        while True:
            # Gather telemetry from all controllers
            ant_pos = await antenna.get_position()
            rf_status = await rf.get_status()
            signal = await receiver.get_signal_quality()
            weather_data = await weather.get_current()
            rec_status = await recording.get_status()
            pwr_status = await power.get_status()

            telemetry = {
                "schedule_id": schedule_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "antenna": {
                    "azimuth": round(ant_pos.azimuth_deg, 2),
                    "elevation": round(ant_pos.elevation_deg, 2),
                },
                "rf": {
                    "frequency_mhz": rf_status.frequency_mhz,
                    "signal_dbm": round(rf_status.signal_strength_dbm, 1),
                    "lock": rf_status.lock,
                    "modulation": rf_status.modulation,
                },
                "signal_quality": {
                    "snr_db": round(signal.get("snr_db", 0), 2),
                    "ber": signal.get("ber", 0),
                    "eb_n0": round(signal.get("eb_n0", 0), 2),
                },
                "weather": {
                    "temp_c": round(weather_data.temperature_c, 1),
                    "humidity_pct": round(weather_data.humidity_pct, 1),
                    "wind_kph": round(weather_data.wind_speed_kph, 1),
                    "rain": weather_data.rain,
                },
                "recording": {
                    "active": rec_status.is_recording,
                    "bytes": rec_status.bytes_recorded,
                },
                "power": {
                    "main": pwr_status.main_power,
                    "ups": pwr_status.ups_active,
                    "battery_pct": pwr_status.battery_pct,
                },
            }

            await websocket.send_text(json.dumps(telemetry))
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        active_connections[schedule_id].discard(websocket)
        if not active_connections[schedule_id]:
            del active_connections[schedule_id]
    except Exception:
        active_connections.get(schedule_id, set()).discard(websocket)
        await websocket.close()
