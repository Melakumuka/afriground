# API_COMPATIBILITY_PLAN.md

## Goal

Preserve the existing customer-facing AfriGround UI and every existing API route while layering the
Phase 1 GSaaS domain on top.

## Compatibility guarantees

1. **No endpoint removed or reshaped.** `/api/v1/commercial/*`, `/api/v1/operations/*`,
   `/api/v1/routing/*`, `/api/v1/data/*`, `/api/v1/support/*`, `/ws/telemetry/*`, `/health`,
   `/api/v1/users/me` all return their current payloads.
2. **Additive DB changes only.** New columns are nullable or defaulted; no legacy table is dropped.
3. **Auth unchanged.** Bearer Supabase JWT verification stays; new tenant context is derived from the
   same token and resolved against the `users`/`organizations` tables.
4. **New routes are additive.** New routers live under their own prefixes:

| Prefix | Purpose |
| --- | --- |
| `/api/v1/tenancy` | Organization info, permissions, roles, audit logs |
| `/api/v1/missions` | Spacecraft, missions, profiles, RF, TM/TC definitions, constraints, SLAs |
| `/api/v1/stations` | Station digital twin: capabilities, hardware, licenses, certifications, time status, agents |
| `/api/v1/contact` | Opportunity chain, reservations, scheduled contacts, observation jobs, receipts |
| `/api/v1/regulatory` | Registration defaults, certification transitions, TX authorization |

5. **Frontend isolation.** The web app computes passes client-side (satellite.js) and uses Next.js
   API routes + Supabase directly — it does not depend on FastAPI endpoints, so it is unaffected.

## Tenant scoping

- New services accept a `TenantContext` (org + user + roles) and filter all reads/writes by
  `org_id`. Cross-tenant access is rejected with 404/403.
- Legacy engines are left untouched in Phase 1; their tenant-scoping is tracked as follow-up work.

## Deployment notes

- `alembic upgrade head` applies the single initial migration on first boot.
- `python scripts/seed_phase1.py` creates the demo tenant data (idempotent).