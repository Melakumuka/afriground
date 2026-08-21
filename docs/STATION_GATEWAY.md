# Station Gateway Architecture

This document describes the AfriGround Station Gateway — the Edge Agent installed locally at a physical ground station.

## 1. Purpose

The Station Gateway is a lightweight, secure application that bridges the AfriGround Cloud control plane with the station's local Mission Control Software (MCS) and equipment. It runs entirely within the station's local network.

**It is NOT:**
- A replacement for the station's existing MCS
- A public-facing web application
- A direct hardware controller

**It IS:**
- A secure cloud client that polls for assigned jobs
- A local operator console for the station engineer
- An adapter layer that translates cloud intent into station-compatible actions
- An artifact collector and execution receipt generator
- An offline-capable job cache

## 2. Application Structure

```
apps/station-gateway/
├── main.py                    # FastAPI application entry point
├── config.py                  # Local configuration (station ID, cloud URL, adapter selection)
├── local_db.py                # SQLite persistence for offline job/profile caching
├── cloud_client.py            # Outbound HTTPS/mTLS client for AfriGround Cloud
├── security.py                # Local authentication, credential storage
│
├── models/                    # Local data models (SQLite-backed)
│   ├── job.py                 # Local job representation
│   ├── profile.py             # Cached StationOperationProfile
│   ├── health.py              # Health snapshot model
│   └── receipt.py             # Local execution receipt
│
├── adapters/                  # Station hardware abstraction layer
│   ├── base_adapter.py        # Abstract StationGatewayAdapter interface
│   ├── mock_zodiac_mcs.py     # MockZodiacMCSAdapter (for testing)
│   └── zodiac_mcs.py          # ZodiacMCSAdapter (placeholder for real RM/RC)
│
├── services/                  # Business logic
│   ├── job_manager.py         # Local job lifecycle, offline queue
│   ├── profile_manager.py     # Profile loading, validation, caching
│   ├── readiness_service.py   # Checklist verification, CONFIRM READY flow
│   ├── health_service.py      # Station health aggregation
│   ├── pass_executor.py       # Pass execution supervisor
│   ├── artifact_service.py    # Artifact collection, checksums, manifest
│   ├── receipt_service.py     # Execution receipt generation
│   └── offline_queue.py       # Event replay after reconnection
│
├── routes/                    # FastAPI routes (local operator console API)
│   ├── operator.py            # Dashboard, pass console HTML serving
│   ├── jobs.py                # Job list, detail, acknowledge
│   ├── equipment.py           # Equipment health display
│   ├── artifacts.py           # Artifact browsing
│   └── health.py              # Health endpoint for local monitoring
│
├── templates/                 # Jinja2 HTML templates (operator console)
│   ├── base.html              # Base layout with Tailwind CSS
│   ├── dashboard.html         # Station overview, next job, health summary
│   ├── jobs.html              # Job list (upcoming, completed, failed)
│   ├── pass_console.html      # THE critical screen: checklist + CONFIRM READY
│   ├── profiles.html          # Saved satellite profiles
│   ├── equipment.html         # Equipment status display
│   ├── alarms.html            # Active alarms and warnings
│   ├── artifacts.html         # Post-pass artifacts and upload status
│   └── settings.html          # Cloud connection, agent identity, config
│
├── static/                    # CSS, JS assets
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image for deployment
└── README.md                  # Local setup instructions
```

## 3. Adapter Interface

The `StationGatewayAdapter` is the abstraction layer between AfriGround's cloud intent and the station's physical equipment.

### Abstract Methods

```python
class StationGatewayAdapter(ABC):
    async def load_station_profile(self, profile_payload: dict) -> bool
    async def load_satellite_profile(self, profile_payload: dict) -> bool
    async def update_ephemeris(self, tle_data: dict) -> bool
    async def prepare_pass(self, job_payload: dict) -> bool
    async def run_preflight_checks(self) -> dict  # Returns check results
    async def get_station_health(self) -> dict
    async def get_equipment_status(self) -> dict
    async def start_pass_recording(self) -> bool
    async def stop_pass_recording(self) -> bool
    async def collect_pass_artifacts(self) -> list  # Returns artifact file paths
    async def get_pass_report(self) -> dict
```

### MockZodiacMCSAdapter
- Returns simulated success for all operations
- Logs intended actions to console
- Simulates pass timeline (AOS → lock acquisition → recording → LOS)
- Generates mock artifact files (pass report, HDR data, ACU log)
- Used for development, testing, CI, and demo mode

### ZodiacMCSAdapter (Future)
- Real integration with PFM730 MCS via RM/RC interface
- Requires vendor ICD: STI 200157
- Maps AfriGround standard intent to MCS-specific operations
- Must not contain hardcoded unsafe commands

## 4. Cloud Communication

The Station Gateway communicates **outbound only** to the AfriGround Cloud.

### Polling Loop
```
Every 30s:
  1. POST /api/v1/edge/heartbeat          → Report alive + health snapshot
  2. GET  /api/v1/edge/jobs/assigned      → Check for new job assignments
  3. POST /api/v1/edge/jobs/{id}/acknowledge → Acknowledge received jobs
```

### Event Push
```
On engineer action:
  POST /api/v1/edge/jobs/{id}/readiness   → Submit READY/NOT_READY

On pass completion:
  POST /api/v1/edge/receipts              → Submit execution receipt
  POST /api/v1/edge/artifacts/upload-request → Get pre-signed upload URLs
```

### Offline Behavior
- If cloud is unreachable, jobs and events are queued locally in SQLite
- On reconnection, queued events are replayed in order
- Expired jobs are never executed
- Jobs outside their authorization window are rejected

## 5. Local Operator Console

The operator console is a server-rendered HTML interface for the station engineer. It is **not** the customer-facing AfriGround portal.

### Dashboard
- Station name and status
- Next scheduled job countdown
- Health summary (MCS, ACU, HDR, time, weather)
- Active alarms
- Cloud connection status

### Pass Console (Critical Screen)
- Job details: satellite name, AOS/LOS, frequency, duration
- Loaded profile summary
- Pre-flight check results (green/red indicators)
- Engineer checklist:
  - ☐ MCS Profile Loaded
  - ☐ HDR Configured
  - ☐ ACU TLE Updated
  - ☐ RF Path Verified
  - ☐ Weather Safe
- **[CONFIRM READY]** button → sends readiness event to cloud
- **[NOT READY]** button → with reason dropdown
- Live status during pass execution

## 6. Security Model

1. The Gateway runs on the station's internal network only
2. No public ports are exposed for inbound connections
3. All cloud communication is outbound HTTPS (with mTLS when available)
4. Local operator console requires authentication (local user/password)
5. Credentials for cloud authentication are stored securely (not in plaintext config)
6. TX is disabled by default; requires explicit regulatory authorization
7. Emergency stop integration: the adapter checks ACU/ADU interlock status
