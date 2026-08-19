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
