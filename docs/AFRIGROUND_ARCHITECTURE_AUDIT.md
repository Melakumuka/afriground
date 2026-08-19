# AFRIGROUND_ARCHITECTURE_AUDIT.md

## Stack

- **Monorepo**: pnpm workspace — `apps/web` (`@afriground/web`), `apps/api`.
- **Web**: Next.js App Router, React 19, Tailwind v4, Three.js, satellite.js. Auth via Supabase client.
- **API**: FastAPI, SQLAlchemy 2 (async/asyncpg), Alembic, Celery+Redis, skyfield/sgp4, GeoAlchemy2 (PostGIS).
- **Storage**: PostgreSQL+PostGIS, Redis, MinIO (S3-compatible).
- **Ops**: Docker Compose for local; `terraform/` exists at root but no active manifests for API/web yet.

## Strengths

- Clean route/service layering (`routes/*` thin, `services/*` business logic, `models/*` ORM).
- Pydantic schemas colocated with services.
- PostGIS geometry + exclusion-ready extensions (`btree_gist`) already provisioned.
- Mock HAL layer enables frontend telemetry demos without hardware.

## Gaps vs. GSaaS OS target

1. **Tenancy**: `Organization` exists but queries are not org-scoped; no RBAC permission model; no audit trail.
2. **Mission**: `SatelliteRFConfig` is a single loose RF blob; no mission, profile, TM/TC definitions, constraints, or SLA.
3. **Station**: `GroundStation` uses JSONB for capabilities; no certification lifecycle, no license, no hardware inventory, no time-sync or agent identity.
4. **Scheduling**: jumps from `PassPrediction` straight to `Booking`/`Schedule`; no opportunity chain, no formal job state machine, no idempotency/eventing.
5. **Safety**: no regulatory enforcement; TX is not gated.

## Recommended adjustments (implemented in Phase 1)

- Organization = tenant; enforce scoping via a tenant context dependency + audit logging.
- Structured Digital Twin & Mission Profile tables (replace JSONB blobs going forward).
- Dedicated orchestrator with a strict `ObservationJob` state machine and transactional outbox.
- `RegulatoryAuthorizationService` as a hard gate; all new stations default `tx_enabled=false`, `REGISTERED`.

## Guardrails (must not break)

- Do not rewrite `apps/web`.
- Do not remove `Booking`/`Schedule`/`Operation` tables (keep for compatibility; migration plan in DATA_MODEL_MIGRATION_PLAN.md).
- Keep all existing API routes returning the same shapes.