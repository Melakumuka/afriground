# Implementation Plan: AfriGround GSaaS Platform (v2)

This document provides the required architectural assessment and phased implementation plan to transform AfriGround into a true **Ground Station Network Operating System**, acting on the Master System Prompt (v2).

## A. Current Architecture & Tech Stack
**Frontend:** Next.js 14/15 App Router (`apps/web`), React 19, TailwindCSS v4, Three.js (`@react-three/fiber`/`drei`) for 3D visualization, `satellite.js` for orbit calculations.
**Backend:** Python 3, FastAPI (`apps/api`), SQLAlchemy (Async), Alembic, Celery for background tasks.
**Database & Infrastructure:** PostgreSQL with PostGIS, Redis (for Celery/caching), MinIO (S3-compatible storage), Docker Compose for local development.
**Monorepo:** PNPM workspace managing `@afriground/web` and the API.

## B. Current Database Schema & API Architecture
The current models provide a foundation but lack commercial GSaaS depth:
- `GroundStation`, `MaintenanceEvent`, `Incident` (Basic location and JSONB metadata, lacking formal certification states or regulatory constraints).
- `Satellite`, `TLESet`, `SatelliteRFConfig`, `Constellation` (Basic RF configs, no full Mission Profile).
- `PassPrediction`, `RecurringMission`, `Booking`, `Schedule`, `Operation` (Rudimentary scheduling, lacking robust job state machines and conflict resolution).
- The API is split into logical routes (`commercial.py`, `operations.py`, `telemetry.py`), utilizing FastAPI dependencies and Celery tasks.

## C. Existing Scheduling/Pass-Prediction Implementation
Pass prediction uses `skyfield` and `sgp4` to generate AOS/LOS times and max elevation (`PassPrediction`). However, it directly jumps to `Booking` and `Schedule`, missing the crucial operational layers: Visibility Opportunity → Contact Opportunity (RF/Elevation constraints) → Customer Reservation → Executable Job. The state machine uses basic string statuses rather than a formal orchestration engine.

## D. Existing Authentication/Authorization & Infrastructure
- **Auth:** Uses Supabase JWT verification (`apps/api/auth.py`), extracting the `sub` (User ID).
- **Infrastructure:** Docker Compose provisions Postgres, Redis, and MinIO locally. No production Kubernetes or Terraform manifests are visible in the immediate active apps directory, though a `terraform` folder exists at the root.

## E. Missing GSaaS Components
1. **Mission Profiles:** Missing comprehensive mission definitions encapsulating RX/TX constraints, telecommand protocols (XTCE), operational blackout periods, and SLA requirements.
2. **Station Digital Twins:** Missing a formal capability model, strict certification pipelines (`REGISTERED` → `PROVISIONING` → ... → `CERTIFIED`), regulatory constraints (geographic auth, power limits), and hardware tracking (SDRs, rotators, time sync).
3. **Contact Planning & Edge Orchestration:** Missing an `afriground-orchestrator` service, strict `ObservationJob` state machine, and asynchronous dispatch mechanisms.
4. **Edge Agent & Time Sync:** Missing the `afriground-station-agent` to bridge cloud and physical stations securely (mTLS), reporting time synchronization and executing jobs.

## F. Recommended Architectural Adjustments
1. **Tenancy:** Enforce `Organization = Tenant`. All backend queries must be tenant-scoped.
2. **Layer 2 Orchestration:** Implement a dedicated asynchronous job orchestrator to manage the complex state transitions of observations, with transactional outbox patterns for events.
3. **Layer 3 Edge Agent Data Foundation:** Prepare the data models for edge agents (identities, heartbeat, time sync quality) before full edge deployment.
4. **Regulatory Enforcement:** Hardcode regulatory checks (frequencies, power, location) via a `RegulatoryAuthorizationService`. Default all new stations to `tx_enabled = false` and `REGISTERED`.

## G. Repository Changes Required
- **Modify:** `apps/api/models/*` to upgrade from basic models to Digital Twins and Mission Profiles, replacing large JSONB blobs with structured tables.
- **Modify:** `apps/api/routes/*` to support the new state machines, job transitions, and tenant-scoping.
- **Create:** Pre-migration documentation (`CURRENT_FUNCTIONALITY.md`, `DATA_MODEL_MIGRATION_PLAN.md`).
- **Create:** `apps/api/services/orchestrator.py` and `apps/api/services/regulatory.py`.
- **Preserve:** The existing customer-facing AfriGround UI (`apps/web`), including the Next.js 3D visualization components and Supabase auth foundation. This UI will be kept and evolved alongside the backend changes, adapting to the new API schemas rather than being replaced.

## H. What Not To Do Yet (Phase 1 Guardrails)
- Do not rewrite the frontend.
- Do not introduce Yamcs deeply yet.
- Do not integrate GNU Radio or SatDump yet.
- Do not build full edge execution capabilities.
- Do not deploy Kubernetes production infra or introduce NATS immediately.
- Do not remove existing Booking/Schedule/Operation tables immediately without a migration plan.
- Do not allow direct hardware control from the web frontend or unrestricted TX.
- Do not make OpenC3 part of the hosted SaaS.

---

## J. Detailed Implementation Plan for Phase 1 (Core Domain Model)

Phase 1 focuses exclusively on laying the rigorous data foundation, state machines, and regulatory rules for a commercial GSaaS, without breaking the existing frontend.

### Phase 1.0 — Audit and Preservation
Produce foundational documents to protect existing UI and API behavior before touching the database.
- Deliver: `CURRENT_FUNCTIONALITY.md`, `AFRIGROUND_ARCHITECTURE_AUDIT.md`, `DATA_MODEL_MIGRATION_PLAN.md`, `STATE_MACHINE_SPEC.md`, `CERTIFICATION_WORKFLOW.md`, `REGULATORY_RULES.md`, `API_COMPATIBILITY_PLAN.md`.

### Phase 1.1 — Tenancy and RBAC
Enforce tenant isolation in backend queries.
- Implement: `Organization/Tenant`, `User`, `Role`, `Permission`, `Tenant context middleware`, `AuditLog`.

### Phase 1.2 — Mission and Spacecraft Model
Separate spacecraft hardware from operational campaigns.
- Implement: `Spacecraft`, `TLESet`, `Mission`, `MissionProfile`, `MissionRFProfile`, `MissionTelemetryDefinition`, `MissionTelecommandDefinition`, `MissionOperationalConstraint`, `MissionSLA`.

### Phase 1.3 — Station Digital Twin & Certification
Replace generic JSONB with structured operational capabilities.
- Implement: `GroundStation`, `StationCapability`, `StationHardware`, `StationLicense`, `StationCertification`, `StationCertificationEvent` (to track transitions auditable), `StationQualityScore`, `StationTimeStatus`, `StationAgentIdentity`.

### Phase 1.4 — Contact Planning and Job State Machine
Implement the full contact-planning chain and strict state transitions.
- Implement Models: `PassPrediction` → `VisibilityOpportunity` → `ContactOpportunity` → `Reservation` → `ScheduledContact` → `ObservationJob` → `ExecutionReceipt`.
- Implement Idempotency & Events: `JobEvent`, `OutboxEvent` (transactional outbox pattern).
- State Transitions: `DRAFT` → `REQUESTED` → `VALIDATING` → `SCHEDULED`/`FAILED` → `QUEUED` → `DISPATCHED` → `ACKNOWLEDGED` → `PREPARING` → `EXECUTING` → `RECEIVING` → `PROCESSING` → `COMPLETED`/`PARTIAL_SUCCESS`/`FAILED`.

### Phase 1.5 — Safety and Regulatory Enforcement
Regulatory compliance as a hard backend constraint.
- Implement: `RegulatoryAuthorizationService`, TX safety defaults (`tx_enabled = false`), License validation, Frequency authorization, Power limits, Certification checks.

### Phase 1.6 — API Contracts, Seeds, and Tests
- Deliver: API schemas, Demo seed data, Simulation-ready domain data, Tenant isolation tests, State machine tests, Regulatory tests, Alembic migration tests.

### Phase 1.7 — Outbox Consumer (Edge Orchestrator seed) — COMPLETE
- Deliver: Transactional-outbox worker (`scripts/outbox_worker.py`) polling PENDING events, webhook dispatch hooks (`services/hooks.py`) for `OBSERVATION_JOB.*`, `EXECUTION_RECEIPT.*`, `STATION.*`, idempotent publishing, FAILED/retry semantics.

### Phase 1.8 — API Integration Tests — COMPLETE
- Deliver: `tests/test_api.py` TestClient route tests (auth deps overridden, real test DB), 403 permission enforcement checks, health/tenancy smoke tests.

> **Phase 1 status: COMPLETE** — 53 tests green; migration `a59283fc1078` applied to dev + test DBs; seed `scripts/seed_phase1.py` idempotent.

---

## K. Detailed Implementation Plan for Phase 2 (Orchestration Runtime & Data Value Chain)

Phase 2 stays inside the Phase 1 guardrails: no full edge execution, no frontend rewrite, no Yamcs/GNU Radio/SatDump/NATS/K8s. It turns the outbox consumer into a real orchestration runtime and completes the observation value chain (mission → contact → job → delivery).

### Phase 2.0 — Orchestration Runtime — COMPLETE
- Implement: shared runtime (`services/orchestration_runtime.py`: `drain`, `SystemJobDriver`, `process_observation_events`, `metrics`); Celery app (`celery_app.py`) + beat task (`tasks.py::drain_outbox`); outbox retry/backoff (`attempt_count`, `next_retry_at`, migration `b5935c0e3f2d`); simulated edge lifecycle driving (`AFRIGROUND_ORCHESTRATION_SIMULATE`); admin metrics endpoint `GET /api/v1/orchestration/metrics`; asyncio worker (`scripts/outbox_worker.py`) shares the same runtime.

### Phase 2.1 — Edge Agent Heartbeat & Time-Sync Ingestion — COMPLETE
- Implement: `services/edge_agent.py` (`EdgeAgentService`: register agent, heartbeat with heartbeat records, time-status ingestion that flags the station twin degraded on large offsets, telemetry ingestion with auto-incident surfacing); system watchdog `check_missed_heartbeats` (flags stations degraded + opens incidents, emits `STATION.DEGRADED`); Celery beat task `orchestration.check_heartbeats`; migration `a4f7c9d1e2b3` adds `station_heartbeats` + `station_telemetry_readings`; edge routes `routes/edge.py`.

### Phase 2.2 — Telemetry & Monitoring — COMPLETE
- Implement: structured telemetry ingestion (`station_telemetry_readings`), `recompute_quality` persisting `StationQualityScore` (availability/reliability/timeliness from heartbeats, SNR, time offsets), quality + telemetry API endpoints; incidents auto-opened on critical telemetry (power loss, SNR floor) with outbox events.

### Phase 2.3 — Data Delivery Pipeline — COMPLETE
- Implement: `services/delivery.py` — on job `COMPLETED` the runtime materializes a dataset (`datasets.observation_job_id`) and executes delivery jobs to every active destination (checksummed, retention expiry), emitting `DATA_DELIVERY.COMPLETED`; idempotent per (dataset, destination).

### Phase 2.4 — End-to-End Simulation & Demo — COMPLETE
- Deliver: `scripts/simulate_edge.py` — self-cleaning scripted edge agent building the full chain (station → mission → contact → job), streaming heartbeat/telemetry, driving `QUEUED → … → COMPLETED` through the runtime, executing delivery, recomputing quality, demonstrating the missed-heartbeat watchdog, and printing a demo timeline.

### Phase 2.5 — Verification — COMPLETE
- Deliver: `tests/test_edge_agent.py`, `tests/test_delivery.py`, endpoint permission tests in `test_api.py`; full suite green (78 tests); migration applied to dev + test DBs; live demo run on the dev DB.

---

## L. Detailed Implementation Plan for Phase 3 (Commercial Value Chain & Integrations)

Phase 3 stays inside the Phase 1 guardrails: no full edge execution, no frontend rewrite, no Yamcs/GNU Radio/SatDump/NATS/K8s. It monetizes the operational runtime from Phase 2: contract usage, SLA enforcement, per-org webhooks, programmatic access, and network-aware routing.

### Phase 3.0 — Commercial Engine & SLA Enforcement — COMPLETE
- Implement: real contract usage aggregation (`CommercialEngine._aggregate_used_minutes` sums completed on-air minutes in the contract window); `RecurringMissionSweeper` auto-generating bookings for active recurring missions from TLE pass predictions (Celery beat `commercial.sweep_recurring` + manual API trigger); `SLAService.enforce_job` evaluating timeliness/latency/success-rate SLAs at job terminal states, recording `sla_violations` idempotently and emitting `SLA.VIOLATION`; business routes `routes/business.py` (contract usage, SLA violations, recurring sweep); migration `c5d6e7f8a9b0`.

### Phase 3.1 — Webhooks & API Keys — COMPLETE
- Implement: per-org webhook fan-out `services/webhooks.py` (`deliver_org_webhooks` runs inside `drain`, HMAC-signed payloads, idempotent `webhook_deliveries` unique per webhook+event); webhook CRUD routes `routes/webhooks.py` (`api.manage`); SHA-256-hashed API keys `services/api_keys.py` (prefix `agk_`, plaintext shown once, scopes + rate-limit tier, `X-API-Key` auth dependency); key management routes `routes/keys.py`; migration `c5d6e7f8a9b0`.

### Phase 3.2 — Network Routing — COMPLETE
- Implement: `services/network_routing.py` computing a composite routing score per station (60% operational risk, 30% measured quality, certification ±, heartbeat freshness ±) with live network ranking; contact planning folds `station_bonus` into opportunity scoring and enforces mission operational constraints (station restrictions, min elevation, blackout windows) via `ContactPlanningService._constraint_block`; routes `routes/network.py`. No schema change (computed from existing twin tables).

### Phase 3.3 — Production Packaging & Liveness — COMPLETE
- Implement: `Dockerfile` (API image, `/healthz` DB-aware liveness probe returning 503 when down), `Dockerfile.worker` (Celery worker + beat), `docker-compose.yml` `api` + `worker` services, `.dockerignore`.

### Phase 3.4 — Verification — COMPLETE
- Deliver: `tests/test_sla.py`, `tests/test_webhooks.py`, `tests/test_api_keys.py`, `tests/test_network_routing.py`, new endpoint permission tests in `test_api.py`; full suite green (102 tests); migration `c5d6e7f8a9b0` applied to dev + test DBs; seed idempotent (adds `api.manage` permission).

---

## M. Detailed Implementation Plan for Phase 4 (Edge Agent & Data Integration Layer)

Phase 4 turns the simulated edge lifecycle into a real machine-facing contract while staying inside the Phase 1 guardrails (no Yamcs/GNU Radio/SatDump/NATS/K8s, no unrestricted TX, no frontend rewrite).

### Phase 4.0 — mTLS Edge Agent Bridge — COMPLETE
- Implement: mTLS identity resolution `services/agent_auth.py` (client-cert CN → `StationAgentIdentity`, rejects unknown/revoked/expired identities); `AgentDispatchService` (`services/agent_dispatch.py`) giving the agent a station-scoped contract: fetch DISPATCHED jobs (with contact window + RF bundle), ACK, drive the execution chain (`ACKNOWLEDGED → PREPARING → EXECUTING → RECEIVING → PROCESSING → terminal`), and submit execution receipts (idempotent per job); agent HTTP routes `routes/agent.py` (`/api/v1/agent/jobs|ack|state|receipt|heartbeat|time-status|telemetry`) — no tenant JWT, the mTLS identity is the authorization.
- Implement runtime integration: `orchestration_runtime.dispatch_due_jobs` transitions QUEUED → DISPATCHED when the contact enters the dispatch lead window (Celery `drain` runs it in real-agent mode); data delivery moved into `SystemJobDriver.advance` so the real agent path triggers the Phase 2.3 pipeline on COMPLETED, not just the simulator.
- Deliver: `scripts/gen_agent_certs.py` (dev CA + server + per-agent client certs via `cryptography`), `entrypoint.sh` (uvicorn mTLS flags: `--ssl-cert-reqs 2`), migration `d6e7f8a9b0c1` adds `certificate_valid_until` + `revoked_at` to `station_agent_identities`; `scripts/agent_sim.py` end-to-end demo (dispatch → fetch → ack → chain → receipt → delivery → watchdog).
- Verify: `tests/test_agent.py` (11 tests) — auth 401s, expired/revoked rejection, station-scoped dispatch, chain validation, receipt idempotency + delivery trigger, dispatch_due_jobs, HTTP endpoint flow; full suite green (113 tests); migration applied to dev + test DBs; live agent demo run on the dev DB.

### Phase 4.1 — Rate Limiting & Webhook Retry (cross-cutting) — COMPLETE
- Implement: `services/rate_limit.py` — Redis-backed sliding-minute token bucket per `APIKey.rate_limit_tier` (standard 60 / pro 600 / enterprise 6000 req/min), returns `{allowed, remaining, limit, reset_after_s}`, fails open with a warning on Redis outage; clients are cached per event loop so pytest/TestClient loops stay isolated; `services/api_keys.get_api_key_context` now enforces the limiter (429 + `Retry-After` via `KeyMeResponse`), `/api/v1/keys/me` surfaces `rate_limit` in the payload.
- Implement: webhook retry/backoff in `services/webhooks.deliver_org_webhooks` — new PUBLISHED outbox events fan out (attempt 1), failed deliveries get `next_retry_at = now + 30 * 2^attempt` (max 5 attempts) and are retried once the window elapses; returns `{delivered, failed, retried}`; migration `e7f8a9b0c1d2` adds `attempt_count` + `next_retry_at` to `webhook_deliveries`.
- Verify: `tests/test_webhooks.py` (retry after window, give-up at max attempts, updated stats dict), `tests/test_api_keys.py` (tier enforcement, fail-open); full suite green (117 tests); migration applied to dev + test DBs; docker redis re-created with host port 6379 mapping.

### Phase 4.2 — Web Frontend Integration — COMPLETE
- Implement: `apps/web/src/lib/api.ts` — server-only FastAPI client that mints a short-lived HS256 Supabase JWT for the provisioned service user (`AFRIGROUND_SERVICE_SUB`, audience `authenticated`, signed with `SUPABASE_JWT_SECRET`) and fails soft (null on any error) so the landing experience survives without the backend; typed helpers for missions, stations, agents, time-status, orchestration metrics, SLA violations, network ranking, datasets, and support tickets.
- Implement: `apps/web/src/app/api/platform/[...path]/route.ts` — catch-all proxy (GET allowlist: missions, stations, orchestration/metrics, business/sla-violations, network/ranking, data/datasets, stations/{id}/time-status|agents; POST only support/tickets, injecting `org_id` from the service env) returning `{ok:true,data}` or 503 `{ok:false}`; `force-dynamic` for Next 16.
- Implement: landing page now renders live mission count / outbox health / SLA violations / queue metrics with a LIVE · API FEED label (`MissionControlPreview` accepts a `MissionControlLive` prop); data catalog shows real datasets (`SAT-<id>` names, processing level, availability) with mock fallback; station page adds a PLATFORM panel (registered edge agents + time-sync offset/clock source) while risk stays simulated; support form submits a real ticket through the proxy and falls back to a simulated TKT reference when the API is unreachable.
- Fix: `support_tickets` was missing `reporter_id` + `category` columns that `services/support_engine.create_ticket` already passed (latent Phase 3.0 schema bug, untested); added both columns to the model, migration `f1a2b3c4d5e6`, and `tests/test_support.py` (create + list-scoped-to-org).
- Fix: repo root `.env` had a stale `DATABASE_URL` (postgres@localhost:5432) that broke the local uvicorn dev server against the docker compose stack (now `afriground@localhost:5433/afriground`); `.env.example` `POSTGRES_PORT` corrected to 5433.
- Verify: `apps/web` production build + TypeScript clean; live proxy smoke test returns real rows for all platform routes including support ticket creation (reporter resolved from JWT sub); support tests green (119 tests total once run).

### Phase 4.3 — Production Infrastructure — COMPLETE
- Implement: `terraform/` provisioning — VPC (public/private/database subnets, NAT, no VPN gateway) + RDS PostgreSQL 16 (Multi-AZ, deletion protection, app-tier-only access) + ElastiCache Redis 7 (private, app-tier-only) + S3 datasets (versioned, public access blocked); ECR repositories with lifecycle policies; ECS Fargate cluster with API (ALB) + Celery worker task definitions wired to SSM Parameter Store secrets (database_url, secret_key, supabase service-role + JWT secrets, optional mTLS certs) and CloudWatch logs; ALB with health check `/healthz` and optional ACM HTTPS listener (HTTP→HTTPS redirect when `acm_certificate_arn` is set); IAM execution/task roles (SSM reads, S3 dataset RW); `outputs.tf` (ALB/RDS/Redis/ECR endpoints) and `bootstrap_state.sh` (S3 state bucket + DynamoDB lock table).
- Apply: run `terraform/bootstrap_state.sh`, then `terraform init` + `terraform apply` with AWS credentials (secrets via `-var` / tfvars); build + push API/worker images to the ECR repos; set `AFRIGROUND_API_URL`, `AFRIGROUND_SERVICE_SUB/ORG`, `SUPABASE_JWT_SECRET` on the Vercel web deployment; point `AFRIGROUND_AGENT_*` mTLS vars on if the agent bridge is enabled.

---

## N. Detailed Implementation Plan for Phase 6 (Real Orbit Dynamics & Booking Integration)

Phase 6 connects the customer-facing `/booking` page to the backend's real SGP4/Skyfield orbital dynamics engine and contact planning state machine, replacing the simulated/Node.js TLE math.

### Phase 6.1 — Booking Page Refactor (Frontend)
- **Current State:** The Booking Page (`apps/web/src/app/[locale]/booking/page.tsx`) searches the public Celestrak NORAD catalog and computes passes using Node's `satellite.js`.
- **Target State:** The Booking Page must act on behalf of a tenant's registered `Mission` and `Spacecraft`.
- **Modifications:**
  - Update Step 1 to fetch and display the user's active missions using the existing `fetchMissions()` proxy, rather than arbitrary NORAD search.
  - When the user selects a Mission and Station, invoke a new backend proxy route that delegates to the FastAPI `/api/v1/contact/visibility` or `/api/v1/contact/plan` endpoints.

### Phase 6.2 — API Proxy Extension
- **Modify:** `apps/web/src/app/api/platform/[...path]/route.ts` to allow POST requests to `/contact/visibility` and `/contact/plan`, ensuring the `org_id` is properly scoped.
- **Modify:** `apps/web/src/lib/api.ts` to add typed client functions `planContact()` and `generateVisibility()`.

### Phase 6.3 — State Machine Execution (Backend)
- **Current State:** The `/booking` page stops at "Quote Request Received" and does nothing on the backend.
- **Target State:** Submitting a booking will now drive the state machine:
  - Generate `VisibilityOpportunity` (via `skyfield`).
  - Generate `ContactOpportunity` (checking station RF/elevation constraints).
  - Generate `Reservation` (status: `REQUESTED`).
- **Validation:** The orchestrator will pick up this reservation and follow the standard contact planning lifecycle.

## User Review Required
> [!IMPORTANT]
> The current booking page allows searching *any* satellite via Celestrak (e.g. ISS). By integrating with the backend GSaaS engine, the booking page will only allow booking passes for **your registered Spacecraft/Missions**. Is this restriction acceptable, or should we automatically provision a Spacecraft/TLE profile on the fly if a user selects a public NORAD catalog ID?

## Verification Plan
1. Ensure the web application compiles cleanly with the new API models.
2. Select a mission in the UI, trigger a pass prediction, and verify that `VisibilityOpportunity` records are successfully created in the Postgres database with accurate AOS/LOS timestamps generated by `skyfield`.

---

## O. Detailed Implementation Plan for Phase 8 (Smart Raw IQ Data Delivery)

Phase 8 completes the end-to-end data pipeline using a **smart routing** model: the Edge Agent delivers data directly to the satellite operator's own cloud storage if they have configured Egress Destinations. Only if no destination is configured does it fall back to AfriGround's internal MinIO store.

```
                         ┌─────────────────────────────────────────┐
                         │       AfriGround Cloud API              │
  [Edge Agent]  ──POST /artifacts/upload-request──▶  checks org's  │
  (pass done)              egress destinations                      │
                         └────────────────┬────────────────────────┘
                                          │
                     ┌────────────────────┴───────────────────────┐
                     │                                            │
          Egress destinations FOUND                   No egress destinations
                     │                                            │
                     ▼                                            ▼
      Returns pre-signed PUT URL                  Returns pre-signed PUT URL
      to CUSTOMER'S own S3/GCS/Azure              to AfriGround INTERNAL MinIO
                     │                                            │
                     ▼                                            ▼
       Edge Agent uploads DIRECTLY               Edge Agent uploads to MinIO
       to customer's cloud bucket               (customer can download later
       ✅ No AfriGround storage cost             via /data/datasets/{id}/download)
```

### Phase 8.1 — Smart Upload Routing (Backend API)
- **Goal:** The `/artifacts/upload-request` endpoint checks if the org has active `DataDeliveryDestination` records. If yes, it generates a pre-signed PUT URL pointing directly to the customer's own cloud. If no destinations exist, it generates a pre-signed PUT URL for AfriGround's internal MinIO.
- **Components:**
  - [MODIFY] `apps/api/routes/edge.py` → `POST /artifacts/upload-request`:
    1. Query `DataDeliveryDestination` for the org (status=active).
    2. **If destinations found:** Build a pre-signed PUT URL for the customer's first (highest-priority) active destination using their stored credentials (S3/GCS/Azure).
    3. **If no destinations:** Fall back to generating a MinIO pre-signed PUT URL for `afriground-raw` bucket.
    4. Return the URL, the target type (`customer_cloud` | `afriground_minio`), and the destination config used.
  - [MODIFY] `apps/api/services/delivery.py` → `on_job_completed`: Update to skip creating simulated `DataDeliveryJob` records if data was already uploaded directly by the Edge Agent (avoid double-delivery).

### Phase 8.2 — Edge Agent Upload Logic
- **Goal:** The Edge Agent calls the routing endpoint, receives the correct URL, and uploads the `.raw` IQ file there.
- **Components:**
  - [MODIFY] `apps/station-gateway/services/execution.py`:
    1. After pass completes, call `POST /api/v1/edge/artifacts/upload-request`.
    2. Read the `upload_url` and `target_type` from the response.
    3. Perform an HTTP PUT of the `.raw` file to that URL.
    4. Log whether data went to `customer_cloud` or `afriground_minio`.

### Phase 8.3 — Fallback Download Links (MinIO path only)
- **Goal:** When data landed in AfriGround MinIO (no egress configured), allow customers to securely download it from the customer portal.
- **Components:**
  - [NEW] `apps/api/routes/data.py`: Add `GET /api/v1/data/datasets/{job_id}/download` — verifies the user owns the job, checks if a `Dataset.storage_url` pointing to MinIO exists, and generates a `get_object` pre-signed URL. Returns `404` if data was uploaded directly to the customer's cloud (no MinIO copy).
  - [MODIFY] `apps/web/src/app/api/platform/[...path]/route.ts`: Proxy the download endpoint.
  - [MODIFY] `apps/web/src/app/[locale]/operations/jobs/[job_id]/page.tsx`: Show "Download Raw IQ" button only when `target_type = afriground_minio`. When `target_type = customer_cloud`, show a message like *"Data delivered directly to your configured cloud destination."*

### Phase 8.4 — Egress Config Credential Security
- **Goal:** Ensure credentials stored in `DataDeliveryDestination` are never exposed in plaintext via the API.
- **Components:**
  - [MODIFY] `apps/api/models/data.py`: Confirm `config` JSONB field stores credentials symmetrically encrypted (AES-256) at rest, using a `DATA_EGRESS_ENCRYPTION_KEY` env variable.
  - [MODIFY] `apps/api/routes/data.py` (destinations list endpoint): Strip `access_key` / `secret_key` / `service_account_json` before returning to the client.

## P. Detailed Implementation Plan for Phase 9 (Alternative 1: Schedule Injection)
*See `docs/ALTERNATIVE_1_SCHEDULE_INJECTION.md` for architectural details. This will be implemented after Phase 8.*

## User Review Required
> [!IMPORTANT]
> **Phase 8 updated** with your smart routing design. The key decision point is in the API:
> - **Operator has configured Egress (S3/GCS/Azure)** → Edge uploads IQ **directly to their cloud**. No AfriGround storage cost. No download button shown.
> - **No Egress configured** → Edge uploads to **AfriGround MinIO**. Customer downloads via a secure link in the portal.
>
> Approve to begin implementation?
