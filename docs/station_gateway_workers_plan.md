# Station Gateway Background Workers & Final Steps

This plan addresses the remaining missing pieces of the Station Gateway Edge Agent: making it "alive" by allowing it to proactively fetch jobs and stream heartbeats, providing documentation, and validating the system integration.

## Proposed Changes

### 1. Cloud Client Extensions
#### [MODIFY] [cloud_client.py](file:///c:/Users/melam/Documents/dev/gsas/afriGround/apps/station-gateway/cloud_client.py)
Add the `report_heartbeat` method to push station telemetry to the cloud endpoint (`POST /stations/{station_id}/agents/{agent_id}/heartbeat`). Add `get_station_profiles` to fetch all certified profiles.

### 2. Background Workers
#### [NEW] [worker.py](file:///c:/Users/melam/Documents/dev/gsas/afriGround/apps/station-gateway/worker.py)
Implement an asynchronous worker loop with two main routines:
- **Sync Routine**: Periodically polls the cloud for assigned jobs and certified profiles. Saves them to the local SQLite database (`CachedJob`, `CachedProfile`). If a job is newly discovered, acknowledges it with the cloud.
- **Heartbeat Routine**: Periodically collects station health (from the `StationGatewayAdapter`) and posts it to the cloud.

### 3. FastAPI Integration
#### [MODIFY] [main.py](file:///c:/Users/melam/Documents/dev/gsas/afriGround/apps/station-gateway/main.py)
Update the FastAPI `lifespan` event to start the background worker loops (`asyncio.create_task()`) when the app starts and cancel them gracefully when the app shuts down.

### 4. Runner Script & Documentation
#### [NEW] [run.sh](file:///c:/Users/melam/Documents/dev/gsas/afriGround/apps/station-gateway/run.sh)
A convenient shell script (and/or powershell equivalent if needed, though uvicorn command works on both) to run the gateway locally via `uvicorn main:app --reload`.
#### [NEW] [README.md](file:///c:/Users/melam/Documents/dev/gsas/afriGround/apps/station-gateway/README.md)
Documentation on configuring the `.env` variables (e.g., `STATION_ID`, `CLOUD_API_URL`) and starting the gateway.

## Verification Plan

### Automated Tests
- Execute `pytest apps/api/tests/test_edge_readiness_flow.py` against the backend to verify the orchestration readiness gates work successfully.

### Manual Verification
- N/A - The automated tests will cover the cloud validation, and I'll review the worker code to ensure logic is sound.
