# CURRENT_FUNCTIONALITY.md — AfriGround (Pre-Migration Audit)

Documentation of the current system behavior before Phase 1 migration. Frozen reference to
guarantee the existing UI and API keep working.

## Scope

- Frontend: Next.js App Router (`apps/web`) — React 19, TailwindCSS v4, Three.js (react-three-fiber/drei), satellite.js.
- Backend: FastAPI (`apps/api`) — Python 3.11, SQLAlchemy 2 async, Alembic, Celery (available), skyfield/sgp4.
- Infra: Postgres + PostGIS, Redis, MinIO (Docker Compose).

## API Surface (current)

| Route | Method | Behavior |
| --- | --- | --- |
| `/health` | GET | Liveness probe. |
| `/api/v1/users/me` | GET | Returns `{user_id, email}` from Supabase JWT. |
| `/api/v1/commercial/quotes` | POST | Create quote from bookings; transitions bookings to `QUOTED`. |
| `/api/v1/commercial/quotes/{id}/accept` | POST | Accept quote; bookings → `RESERVED`. |
| `/api/v1/commercial/contracts` | POST | Create enterprise contract. |
| `/api/v1/commercial/contracts/{id}` | GET | Contract usage. |
| `/api/v1/commercial/recurring-missions` | POST | Create recurring mission (booking auto-gen is a TODO). |
| `/api/v1/operations/maintenance` | POST | Create maintenance window; counts affected schedules. |
| `/api/v1/operations/maintenance/{station_id}` | GET | List maintenance (upcoming only by default). |
| `/api/v1/operations/incidents` | POST | Open incident. |
| `/api/v1/operations/incidents` | GET | List incidents (open only by default). |
| `/api/v1/operations/incidents/{id}/status` | PATCH | Transition incident status (validated). |
| `/api/v1/operations/stations/{id}/risk` | GET | Composite risk score (availability/reliability/weather/connectivity/maintenance). |
| `/api/v1/routing/failover/{schedule_id}` | POST | Migrate schedule to alternate station. |
| `/ws/telemetry/{schedule_id}` | WS | Streamed mock telemetry from HAL mock controllers. |

## Domain models (current tables)

- `roles`, `organizations`, `users`, `contracts`, `quotes`
- `satellites`, `tle_sets`, `satellite_rf_configs`, `constellations`, `constellation_satellites`, `constellation_tasking`
- `ground_stations`, `maintenance_events`, `incidents`
- `pass_predictions`, `recurring_missions`, `bookings`, `schedules`, `operations`
- `datasets`, `data_delivery_destinations`, `data_delivery_jobs`, `api_keys`, `webhooks`, `support_tickets`

## Behavior notes

- Auth: Bearer JWT verified against `SUPABASE_JWT_SECRET` (HS256, audience `authenticated`). `sub` = user id.
- Pass prediction: `SGP4Engine` (skyfield) → `PassPrediction` rows (AOS/LOS/max elevation/duration).
- Booking flow is string-status based: `DRAFT → REQUESTED → QUOTED → RESERVED → CONFIRMED → CANCELLED → EXPIRED`.
- No tenant scoping: services query without org filter.
- No station certification, mission profiles, TX safety, or job state machine yet.
- Frontend computes its own passes client-side (satellite.js) and does not call the FastAPI pass endpoints.