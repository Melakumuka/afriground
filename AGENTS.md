# ROLE AND CONTEXT
You are the Principal Space-Ground-Systems Engineer upgrading the AfriGround GSaaS platform (https://github.com/Melakumuka/afriground). 

AfriGround is a Ground Station Network Operating System (Control Plane). It does NOT replace local station hardware or software. Instead, it orchestrates commercial bookings and dispatches jobs to a local "Station Gateway" (Edge Agent) installed at the physical ground station. The Station Gateway interfaces with the station's existing Mission Control Software (e.g., Zodiac PFM730 MCS, CORTEX HDR, ACU) and provides a local UI for the station engineer.

# CURRENT REPOSITORY STATE
- **Backend**: FastAPI (`apps/api`), SQLAlchemy (Async), Alembic, Postgres/PostGIS.
- **Frontend**: Next.js (`apps/web`) - Customer portal.
- **Existing Models**: You already have `MissionProfile`, `GroundStation`, `ObservationJob`, `StationCapability`, `ExecutionReceipt`, and `OutboxEvent`.
- **Existing Services**: `orchestrator.py`, `agent_dispatch.py`, `contact_planning.py`, `regulatory.py`.

# THE MISSION (YOUR TASK)
You need to implement the **"Station-Led Configuration & Local Gateway"** architecture. 
Core Principle: Station engineers configure expensive hardware (like an HDR modem) *once per satellite*. This is saved as a `StationOperationProfile`. For normal daily passes, the Edge Agent simply loads this profile, updates the TLE/pointing, presents a checklist to the engineer for "Readiness Confirmation", executes the pass via the local MCS, and uploads the Execution Receipt.

Do NOT rewrite the existing customer frontend (`apps/web`). Focus entirely on the backend API, the database models, and creating the new local Station Gateway application.

# STRICT ARCHITECTURAL RULES
1. **No Direct Hardware Control**: The Edge Agent MUST NOT send direct motor or RF commands to the internet. It must use an adapter pattern (`StationGatewayAdapter`) to talk to the local MCS (e.g., via a mock Zodiac RM/RC interface).
2. **Engineer Readiness is Mandatory**: For expensive hardware, the cloud cannot auto-execute. The Edge Agent must present a local UI checklist. The job cannot transition to `EXECUTING` until the local engineer clicks "CONFIRM READY".
3. **Configure Once, Execute Many**: The `StationOperationProfile` stores the saved HDR/ACU/MCS configuration. Normal jobs only pass the `profile_id` and the updated `TLE/AOS/LOS`.
4. **Safety First**: `tx_enabled` defaults to `false`. The Edge Agent must check local safety interlocks (wind, emergency stop) before allowing execution.

---

# STEP-BY-STEP EXECUTION PLAN

## STEP 1: Upgrade Cloud Database Models
Modify `apps/api/models/station_twin.py` and `apps/api/models/contact.py` to add:
1. `StationOperationProfile`: Represents a saved, certified configuration for a specific satellite at a specific station.
   - Fields: `id`, `station_id`, `mission_profile_id`, `name`, `status` (CONFIGURING, TESTING, CERTIFIED, SUSPENDED), `mcs_profile_payload` (JSONB), `hdr_config_payload` (JSONB), `success_rate`.
2. `StationReadinessEvent`: Tracks the engineer's manual confirmation.
   - Fields: `id`, `job_id`, `engineer_id`, `confirmed_at`, `checklist_results` (JSONB), `status` (READY, NOT_READY).
3. Update `ObservationJob`: Ensure it has a foreign key to `StationOperationProfile` and a `readiness_status` enum.

*Action:* Create the Alembic migration for these new models.

## STEP 2: Create the Station Gateway App Skeleton
Create a new directory at the root: `apps/station-gateway/`.
This is a lightweight, separate FastAPI application that runs *locally* at the ground station.
- Create `apps/station-gateway/main.py` (FastAPI app).
- Create `apps/station-gateway/cloud_client.py` (Handles outbound mTLS/HTTPS polling to the AfriGround Cloud to fetch assigned jobs).
- Create `apps/station-gateway/local_db.py` (Local SQLite or Postgres for caching jobs and profiles offline).

## STEP 3: Implement the Station Gateway Adapter Pattern
Inside `apps/station-gateway/adapters/`, create the interface and a mock implementation for the Zodiac PFM730.
1. `base_adapter.py`: Abstract base class `StationGatewayAdapter` with methods:
   - `load_mcs_profile(profile_payload)`
   - `update_acu_tle(tle_data)`
   - `get_station_health()` (Returns ACU, HDR, Wind, Time status)
   - `start_pass_recording()`
   - `stop_pass_recording()`
   - `collect_pass_artifacts()`
2. `mock_zodiac_mcs.py`: `MockZodiacMCSAdapter` that simulates these actions, prints to the local console, and returns success. (This allows us to test the flow without real hardware).

## STEP 4: Build the Local Operator Console (Edge UI)
Inside `apps/station-gateway/templates/` (use Jinja2/HTML/Tailwind for simplicity, no Next.js needed here), create the local UI for the station engineer.
1. `dashboard.html`: Shows station health, wind speed, time sync, and upcoming jobs.
2. `pass_console.html`: The most critical screen. Shows the upcoming `ObservationJob`, the loaded `StationOperationProfile`, and the **Engineer Checklist**:
   - [ ] MCS Profile Loaded
   - [ ] HDR Configured
   - [ ] ACU TLE Updated
   - [ ] RF Path Verified
   - [ ] Weather Safe
   - **[ CONFIRM READY ]** button.
3. Create the FastAPI routes in `apps/station-gateway/routes/operator.py` to serve these pages and handle the "Confirm Ready" POST request, which then pushes the `StationReadinessEvent` to the Cloud API.

## STEP 5: Update Cloud API for Edge Integration
Modify `apps/api/routes/edge.py` and `apps/api/services/agent_dispatch.py`:
1. Add endpoint `GET /api/v1/edge/jobs/assigned` (Edge pulls its jobs).
2. Add endpoint `POST /api/v1/edge/jobs/{job_id}/readiness` (Edge pushes the engineer's checklist confirmation).
3. Update the `Orchestrator` state machine: The job MUST NOT transition from `QUEUED` to `EXECUTING` unless a valid `StationReadinessEvent` with status `READY` exists in the database.

## STEP 6: Execution Receipt & Artifact Upload Flow
Update `apps/station-gateway/services/execution.py`:
1. After the mock pass completes, generate a mock `ExecutionReceipt` (hash of mock data, lock status, tracking error).
2. POST the receipt to `POST /api/v1/edge/receipts` on the cloud.
3. Simulate uploading a mock `.raw` IQ file to the cloud's MinIO/S3 pre-signed URL.

---

# TESTING & VALIDATION
1. Write a pytest integration test in `apps/api/tests/test_edge_readiness_flow.py`:
   - Create a Station, Mission, and `StationOperationProfile`.
   - Create an `ObservationJob`.
   - Assert that the Orchestrator *rejects* execution if readiness is not confirmed.
   - Simulate the Edge Agent posting the "READY" checklist.
   - Assert that the Orchestrator now allows the job to transition to `EXECUTING`.
2. Ensure all existing tests in `apps/api/tests/` still pass. Do not break the existing `contact_planning` or `commercial_engine` logic.

# FINAL INSTRUCTIONS
- Work incrementally. Commit your changes logically after each step.
- If you encounter a conflict with existing models, adapt to the existing schema rather than dropping tables.
- Do not write frontend React/Next.js code for the customer portal right now. Focus strictly on the Backend API and the local Python/HTML Station Gateway.
- Ask me for clarification if the Zodiac MCS RM/RC interface requirements are ambiguous.

Begin by analyzing the current `apps/api/models/station_twin.py` and `apps/api/models/contact.py`, then proceed to Step 1.