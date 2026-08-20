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

### Phase 4.3 — Production Infrastructure — PLANNED
- Complete `terraform/` provisioning (Postgres/Redis/MinIO), API + worker images with mTLS, Vercel API deployment, secrets management.
