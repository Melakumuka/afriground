# AfriGround — Phase 1 → 4 Walkthrough

A detailed, commit-grounded walkthrough of everything built from Phase 1 (Core
Domain Model) through Phase 4 (Edge Agent & Data Integration Layer), including the
production rollout that took the platform live. Companion to
`implementation_plan.md` (the plan), `CURRENT_FUNCTIONALITY.md` (API surface),
and `aws_deployment_plan.md` (infrastructure).

## How to read this

Each phase section describes: **goal → what was built (models / services / routes /
scripts / tests / migrations) → status**. Phase boundaries follow the actual git
history of the repository, so each section is anchored to real commits.

---

## Phase 0 — Starting point (the "before" state)

The pre-migration codebase was a functional but shallow GSaaS:
- **Frontend:** Next.js App Router (`apps/web`), React 19, TailwindCSS v4,
  Three.js (react-three-fiber/drei), satellite.js — a polished cinematic landing,
  telemetry, scheduling wizard, and data catalog with **simulated** data.
- **Backend:** FastAPI (`apps/api`), SQLAlchemy async, Alembic, Celery.
- **Schema:** basic `GroundStation`, `Satellite`, `TLESet`, `PassPrediction`,
  `Booking`, `Schedule`, `Operation`; booking flow was string-status based
  (`DRAFT → REQUESTED → QUOTED → RESERVED → CONFIRMED → CANCELLED → EXPIRED`).
- **No** tenant scoping, station certification, mission profiles, TX safety, job
  state machine, or edge agent support.
- **Auth:** Supabase JWT verification only (`sub` = user id).

**Preservation guardrails** (from the plan): the existing UI was *kept and evolved*,
never rewritten; Yamcs / GNU Radio / SatDump / NATS / Kubernetes were explicitly out
of scope; no unrestricted TX from the web.

---

## Phase 1 — Core Domain Model  `502ec09`

**Goal:** lay the rigorous data foundation: tenancy, digital twins, regulatory
enforcement, and a real contact-planning → job state machine — without breaking the
existing UI.

### 1.0 Audit & preservation
Produced the pre-migration docs that still live in `docs/`:
`CURRENT_FUNCTIONALITY.md`, `AFRIGROUND_ARCHITECTURE_AUDIT.md`,
`DATA_MODEL_MIGRATION_PLAN.md`, `STATE_MACHINE_SPEC.md`,
`CERTIFICATION_WORKFLOW.md`, `REGULATORY_RULES.md`, `API_COMPATIBILITY_PLAN.md`.

### 1.1 Tenancy & RBAC
- New `Organization` (= tenant), `User`, `Role`, `Permission`, `RolePermission`,
  `AuditLog` tables (`models/tenancy.py`, `models/core.py`).
- `TenantContext` + `get_tenant_context` dependency (`services/tenancy.py`) — every
  service and route is now org-scoped; `write_audit_log` records admin actions.
- Permission checks via `tenant.require_permission(...)` and `require_org()`.

### 1.2 Mission & spacecraft model
- `Spacecraft` separated from hardware `Satellite`; `TLESet` for orbit elements.
- `Mission`, `MissionProfile`, `MissionRFProfile` (band, freq, modulation, symbol
  rate, power, polarization), `MissionTelemetryDefinition`, `MissionTelecommandDefinition`,
  `MissionOperationalConstraint` (e.g. min elevation, blackouts), `MissionSLA`.

### 1.3 Station digital twin & certification
- Replaced generic JSONB with structured twin tables: `GroundStation`,
  `StationCapability` (band/freq/power/polarization per band),
  `StationHardware`, `StationLicense`, `StationQualityScore`,
  `StationTimeStatus`, `StationAgentIdentity` (foundation for Phase 4).
- Formal certification state machine: `StationCertification` +
  `StationCertificationEvent` (REGISTERED → PROVISIONING → VALIDATING → CERTIFIED /
  REJECTED), driven by `services/regulatory.py`.

### 1.4 Contact planning & job state machine
- Full chain modeled: `PassPrediction → VisibilityOpportunity → ContactOpportunity →
  Reservation → ScheduledContact → ObservationJob → ExecutionReceipt`
  (`models/contact.py`, `models/scheduling.py`).
- `ContactPlanningService` (`services/contact_planning.py`): generate visibility,
  create opportunities, reserve, confirm, schedule contacts.
- `ObservationOrchestrator` (`services/orchestrator.py`) creates executable jobs
  with the strict transition chain:
  `DRAFT → REQUESTED → VALIDATING → SCHEDULED/FAILED → QUEUED → DISPATCHED →
  ACKNOWLEDGED → PREPARING → EXECUTING → RECEIVING → PROCESSING → COMPLETED /
  PARTIAL_SUCCESS / FAILED`.
- Transactional outbox: `OutboxEvent` + `JobEvent` (durable events committed with
  their owning transaction).

### 1.5 Safety & regulatory enforcement
- `RegulatoryAuthorizationService`: TX-safety defaults (`tx_enabled = false`),
  license validation, frequency authorization, power limits, certification checks
  before a station may transmit.

### 1.6–1.8 API contracts, seeds, outbox consumer, tests
- `scripts/seed_phase1.py` — idempotent demo seed (orgs, users, ISS satellite,
  mission, Cape Town station, contact chain → job).
- `scripts/outbox_worker.py` — transactional-outbox worker polling PENDING events;
  `services/hooks.py` webhook dispatch for `OBSERVATION_JOB.*`, `EXECUTION_RECEIPT.*`,
  `STATION.*` with idempotent publishing and FAILED/retry semantics.
- `tests/test_api.py` — route tests with real test DB + permission enforcement.

> **Status: COMPLETE** — 53 tests green; migration `a59283fc1078`; seed idempotent.

---

## Phase 2 — Orchestration Runtime & Data Value Chain  `4d6e184`, `1651daf`

**Goal:** turn the outbox consumer into a real orchestration runtime and complete the
observation value chain: mission → contact → job → delivery.

### 2.0 Orchestration runtime
- `services/orchestration_runtime.py`: shared `drain` loop, `SystemJobDriver`
  advancing jobs through their states, `process_observation_events`,
  `metrics` (outbox health / backpressure).
- Celery app + beat task `tasks.py::drain_outbox`; outbox retry/backoff via
  `attempt_count` / `next_retry_at` (migration `b5935c0e3f2d`).
- Simulated edge lifecycle driving (`AFRIGROUND_ORCHESTRATION_SIMULATE=1`) so the
  whole chain runs without physical hardware.
- Admin endpoint `GET /api/v1/orchestration/metrics`; the asyncio
  `outbox_worker.py` shares the same runtime.

### 2.1 Edge agent heartbeat & time-sync ingestion
- `services/edge_agent.py`: register agent, heartbeat records, time-status ingestion
  (flags the station twin DEGRADED on large offsets), telemetry ingestion with
  auto-incident surfacing.
- Watchdog `check_missed_heartbeats` (flags stations + opens incidents, emits
  `STATION.DEGRADED`); Celery beat `orchestration.check_heartbeats`.
- Migration `a4f7c9d1e2b3` adds `station_heartbeats` + `station_telemetry_readings`;
  edge routes `routes/edge.py`.

### 2.2 Telemetry & monitoring
- Structured telemetry ingestion; `recompute_quality` persists `StationQualityScore`
  (availability / reliability / timeliness derived from heartbeats, SNR, time
  offsets); quality + telemetry API endpoints; auto-incidents on critical telemetry
  (power loss, SNR floor) with outbox events.

### 2.3 Data delivery pipeline
- `services/delivery.py`: on job COMPLETED the runtime materializes a `Dataset`
  (linked via `observation_job_id`) and runs delivery jobs to every active
  destination (`DataDeliveryDestination`) — checksummed, retention expiry, emitting
  `DATA_DELIVERY.COMPLETED`; idempotent per (dataset, destination).

### 2.4 End-to-end simulation
- `scripts/simulate_edge.py` — self-cleaning scripted edge agent: builds the full
  chain, streams heartbeat/telemetry, drives `QUEUED → … → COMPLETED` through the
  runtime, executes delivery, recomputes quality, demonstrates the missed-heartbeat
  watchdog, prints a demo timeline.

> **Status: COMPLETE** — 78 tests green; migrations applied; live demo run on dev DB.

---

## Phase 3 — Commercial Value Chain & Integrations  `ac87c45`

**Goal:** monetize the Phase 2 runtime: contract usage, SLA enforcement, per-org
webhooks, programmatic access (API keys), and network-aware routing.

### 3.0 Commercial engine & SLA enforcement
- `CommercialEngine._aggregate_used_minutes` — real contract usage from completed
  on-air minutes in the contract window.
- `RecurringMissionSweeper` — auto-generates bookings for active recurring missions
  from TLE pass predictions (Celery beat `commercial.sweep_recurring` + manual API
  trigger).
- `SLAService.enforce_job` — evaluates timeliness/latency/success-rate SLAs at job
  terminal states, records `sla_violations` idempotently, emits `SLA.VIOLATION`.
- Business routes `routes/business.py` (contract usage, SLA violations, recurring
  sweep). Migration `c5d6e7f8a9b0`.

### 3.1 Webhooks & API keys
- Per-org webhook fan-out `services/webhooks.py` (HMAC-signed payloads, idempotent
  `webhook_deliveries` unique per webhook+event); CRUD routes `routes/webhooks.py`
  (permission `api.manage`).
- SHA-256-hashed API keys `services/api_keys.py` (prefix `agk_`, plaintext shown
  once, scopes + rate-limit tier, `X-API-Key` auth dependency); key management
  routes `routes/keys.py`. Same migration `c5d6e7f8a9b0`.

### 3.2 Network routing
- `services/network_routing.py` — composite routing score per station (60% operational
  risk, 30% measured quality, certification ±, heartbeat freshness ±) with a live
  network ranking endpoint; contact planning folds `station_bonus` into opportunity
  scoring and enforces mission operational constraints (station restrictions, min
  elevation, blackouts) via `ContactPlanningService._constraint_block`.
  No schema change (computed from existing twin tables).

### 3.3 Production packaging
- `Dockerfile` (API image, DB-aware `/healthz` returning 503 when the DB is down),
  `Dockerfile.worker` (Celery worker + beat), `docker-compose.yml` `api` + `worker`
  services, `.dockerignore`.

> **Status: COMPLETE** — 102 tests green; migration applied; seed adds `api.manage`.

---

## Phase 4 — Edge Agent & Data Integration Layer  `6932b0e`, `c7ed0a7`, `bbafdc3`, `7464b15`

**Goal:** turn the simulated edge lifecycle into a real machine-facing contract and
connect the whole platform to the live web frontend and production infrastructure.

### 4.0 mTLS edge agent bridge
- `services/agent_auth.py` — mTLS identity resolution: client-cert CN → 
  `StationAgentIdentity`; rejects unknown / revoked / expired identities.
- `AgentDispatchService` (`services/agent_dispatch.py`) — station-scoped agent
  contract: fetch DISPATCHED jobs (contact window + RF bundle), ACK, drive the
  execution chain (`ACKNOWLEDGED → PREPARING → EXECUTING → RECEIVING → PROCESSING →
  terminal`), submit idempotent execution receipts.
- Agent HTTP routes `routes/agent.py` (`/api/v1/agent/jobs|ack|state|receipt|
  heartbeat|time-status|telemetry`) — **no tenant JWT; the mTLS identity IS the
  authorization**, every operation scoped to the agent's own station.
- Runtime integration: `orchestration_runtime.dispatch_due_jobs` transitions
  QUEUED → DISPATCHED in the dispatch lead window; data delivery moved into
  `SystemJobDriver.advance` so the real-agent path triggers the Phase 2.3 pipeline
  on COMPLETED.
- Tooling: `scripts/gen_agent_certs.py` (dev CA + server + per-agent client certs),
  `entrypoint.sh` runs uvicorn with `--ssl-cert-reqs 2`; migration `d6e7f8a9b0c1`
  adds `certificate_valid_until` + `revoked_at`; `scripts/agent_sim.py` end-to-end
  demo (dispatch → fetch → ack → chain → receipt → delivery → watchdog).

> **Status: COMPLETE** — 113 tests green (11 new for the agent bridge).

### 4.1 Rate limiting & webhook retry (cross-cutting)
- `services/rate_limit.py` — Redis-backed sliding-minute token bucket per
  `APIKey.rate_limit_tier` (standard 60 / pro 600 / enterprise 6000 req/min),
  returns `{allowed, remaining, limit, reset_after_s}`, fails open on Redis outage;
  `get_api_key_context` enforces it (429 + `Retry-After`); `/api/v1/keys/me`
  surfaces the limit. Migration `e7f8a9b0c1d2`.
- Webhook retry/backoff: PUBLISHED outbox events fan out (attempt 1); failed
  deliveries retry at `now + 30 * 2^attempt` (max 5 attempts); returns
  `{delivered, failed, retried}`.

> **Status: COMPLETE** — 117 tests green.

### 4.2 Web frontend integration  `bbafdc3`
- `apps/web/src/lib/api.ts` — server-only FastAPI client: mints a short-lived HS256
  Supabase JWT for the provisioned service user (`AFRIGROUND_SERVICE_SUB`, audience
  `authenticated`, signed with `SUPABASE_JWT_SECRET`); **fails soft** (null on any
  error) so the landing experience survives without the backend. Typed helpers for
  missions, stations, agents, time-status, orchestration metrics, SLA violations,
  network ranking, datasets, support tickets.
- `apps/web/src/app/api/platform/[...path]/route.ts` — catch-all proxy (GET allowlist
  + POST `support/tickets`, injecting `org_id`), returns `{ok:true,data}` or
  `503 {ok:false}`; `force-dynamic` for Next 16.
- **Landing** renders live mission count / outbox health / SLA violations with a
  `LIVE · API FEED` label (`MissionControlPreview` accepts a `MissionControlLive`
  prop); **data catalog** shows real datasets (`SAT-<id>`, processing level,
  availability) with mock fallback; **station page** adds a PLATFORM panel
  (registered edge agents + time-sync offset/clock source) while risk stays
  simulated; **support form** submits a real ticket through the proxy and falls back
  to a simulated TKT reference when the API is unreachable.
- **Latent bug fixed:** `support_tickets` was missing `reporter_id` + `category`
  columns that `support_engine.create_ticket` already passed — added both, migration
  `f1a2b3c4d5e6`, plus `tests/test_support.py`.
- **Local dev fix:** repo-root `.env` had a stale `DATABASE_URL` breaking the local
  uvicorn dev server against the compose stack; `.env.example` `POSTGRES_PORT`
  corrected to 5433.

> **Status: COMPLETE** — web build + TS clean; live proxy smoke test returns real
> rows; 119 tests total.

### 4.3 Production infrastructure  `7464b15`
- `terraform/` (planned ECS path): VPC (public/private/database subnets, NAT), RDS
  PostgreSQL 16 (Multi-AZ, deletion protection, app-tier-only access), ElastiCache
  Redis 7 (private, app-tier-only), S3 datasets (versioned, public access blocked);
  ECR repos with lifecycle policies; ECS Fargate API (ALB) + Celery worker task
  definitions wired to SSM Parameter Store secrets and CloudWatch logs; ALB health
  check on `/healthz` with optional ACM HTTPS listener; IAM execution/task roles;
  `outputs.tf` + `bootstrap_state.sh` (S3 state bucket + DynamoDB lock).

> **Status: CODE-COMPLETE (planned path).** The *running* deployment instead uses the
> free-tier path below.

---

## Post-Phase-4 production rollout (the live system)

### 4.4 Free-tier AWS stack (Tokyo)  `2f8a22b`, `b860e3a`, `6d415eb`, `d34a605`
Provisioned `terraform/free/` in `ap-northeast-1` (free-tier eligible) at **≈ $0/mo**:
t3.micro EC2 host (Docker, api + worker containers), `db.t3.micro` PostgreSQL 16.14
(+PostGIS, 60 tables, alembic at `f1a2b3c4d5e6`), `cache.t3.micro` Redis 7.1,
S3 (`afriground-free-repo`, `afriground-free-datasets`), SSM params under
`/afriground/free/*`. Secrets land in SSM, then in `/opt/afriground/.env` on the host.
- **API live:** `http://13.231.123.242:8000` (healthz OK, tenant-scoped surface).
- **DB seeded** with the fixed demo identity the web proxy's JWT sub/org expect
  (`b569d5d7-…` / `9b6b697e-…`), admin bound to `Platform Admin`.
- **Worker:** celery + beat in the same stack; `drain_outbox` runs on schedule.
- **Host management:** SSM `send-command` (operator network blocks direct ports;
  SSH key kept out of the repo).
- **Web live:** https://afriground.vercel.app (Vercel Auth disabled → public domain;
  env: `AFRIGROUND_API_URL`, service sub/org, JWT secret).

### 4.5 Hydration error #418 fix  `e93b653`
- **Root cause:** `PassSimulatorWidget.tsx:181` formatted a fixed mock time with
  `toLocaleTimeString()` and no timezone → Vercel (UTC) rendered `06:42:15 PM`, the
  UTC+8 browser rendered `02:42:15 AM` → server/client text mismatch → #418.
- **Fix:** every date/time render now forces `timeZone: "UTC"` (PassSimulatorWidget,
  data page, station page, booking page).
- **Verified** by reproducing with a `TZ=UTC` dev server + Playwright
  (`timezoneId: "Asia/Shanghai"`), and by checking prod HTML serves `18:42:15 UTC`.

### 4.6 Secrets hygiene  `efdafea`
- `docker-compose.yml`: every credential via `${VAR:?}` from the gitignored `.env`;
  `.env.example` documents the surface; AWS runtime secrets stay in SSM/Vercel.
- `apps/api/scripts/_env.py` (new shared loader) + all scripts/tasks/config/tests
  read URLs from env with passwordless localhost fallbacks.
- Deleted the local `terraform/free/terraform.tfvars`; docs gained the `TF_VAR_*`
  workflow and a "Secrets hygiene" section.
- **AWS CLI credentials** moved from `~/.aws/credentials` into User-level env vars
  (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_DEFAULT_REGION`); the
  credentials file was deleted.
- Ripgrep sweep confirmed zero embedded secrets remain in the tree.

### 4.7 Demo data enrichment  `7ae499e`, `d6d3fe8`
New idempotent `scripts/seed_demo_rich.py` run inside the API container:
- **Missions 1 → 3** (Demo LEO Observation, Atlantic Weather Relay, CropWatch
  Africa) with satellites NOAA-19 + SAOCOM-1A and TLE sets.
- **SLA violations 0 → 3** (2 VIOLATED + 1 RESOLVED, unit `%`) → live alert feed.
- **Datasets 0 → 6** (MULTISPECTRAL / OPTICAL / SAR / HYPERSPECTRAL, L0–L2A).
- **Stations 1 → 3** (Cape Town, Johannesburg, Durban) with quality scores →
  live network ranking.
- **Edge agents + time-status on every station** so the station PLATFORM panel is
  populated regardless of station ordering.
- `_env.py` hardened to be container-safe (no repo-root `.env` inside the image).

### 4.8 JWT secret rotation  (2026-08-21 session)
- The demo/service JWT secret (`mockjwtsecret`) rotated to a fresh 64-char random
  value, rolled out in order: SSM param → instance `/opt/afriground/.env` +
  container recreation → verified (new secret 200 / old secret 401) → Vercel env +
  redeploy + prod alias re-pointed → local `.env` files.
- Value is **not** in the repo; it lives only in SSM, `/opt/afriground/.env`, and
  the Vercel project env.

---

## Where the platform stands today

| Layer | State |
| --- | --- |
| Web | https://afriground.vercel.app — live API feed (3 ACTIVE / OUTBOX HEALTHY / 3 VIOLATIONS + alerts), 6 datasets, 3-station ranking, per-station agents & time-sync |
| API + worker | EC2 `i-0ba87f670fcf5d059` (t3.micro) — `http://13.231.123.242:8000` |
| DB / cache / storage | RDS Postgres 16 + PostGIS (60+ tables) / ElastiCache Redis 7 / S3 |
| Identity & secrets | SSM `/afriground/free/*` + Vercel env + `/opt/afriground/.env` (rotated) |
| Tests | 119 backend tests across Phase 1–4.2 |
| Repository | clean working tree, all session commits pushed to `origin/main` |

**Natural next steps** (not yet done): real TLE pass predictions for `/booking`,
scoping the IAM deploy user below AdministratorAccess, HTTPS for the API, and the
ECS/ALB migration once the free tier is exhausted.