# DATA_MODEL_MIGRATION_PLAN.md

## Principles

- **Additive first**: Phase 1 introduces new tables and *adds columns* to existing tables. No drops.
- **Compatibility**: legacy tables (`bookings`, `schedules`, `operations`, `pass_predictions`) remain readable and writable by the old routes.
- **Single initial migration**: the local DB is greenfield (no application tables), so `0001` creates the full schema (legacy + Phase 1).
- **Migration testing**: `tests/test_migration.py` runs `alembic upgrade head` against a dedicated test database.

## Legacy tables — kept unchanged

`roles`, `organizations`, `users`, `contracts`, `quotes`, `satellites`, `tle_sets`,
`satellite_rf_configs`, `constellations`, `constellation_satellites`, `constellation_tasking`,
`ground_stations`, `maintenance_events`, `incidents`, `pass_predictions`, `recurring_missions`,
`bookings`, `schedules`, `operations`, `datasets`, `data_delivery_destinations`,
`data_delivery_jobs`, `api_keys`, `webhooks`, `support_tickets`.

## Modified tables (additive columns)

- `organizations`: `+is_active BOOLEAN default true`
- `users`: `+is_active BOOLEAN default true`
- `roles`: `+is_system BOOLEAN default false`, `+description TEXT`
- `ground_stations`: `+org_id UUID FK organizations` (operator), `+certification_state VARCHAR(50) default 'REGISTERED'`,
  `+tx_enabled BOOLEAN default false`, `+registration_date TIMESTAMPTZ`, `+operator_contact_email VARCHAR(255)`

## New Phase 1 tables

### Tenancy & RBAC (`models/tenancy.py`)
`permissions`, `role_permissions`, `audit_logs`

### Mission & Spacecraft (`models/mission.py`)
`spacecraft`, `missions`, `mission_profiles`, `mission_rf_profiles`, `mission_telemetry_definitions`,
`mission_telecommand_definitions`, `mission_operational_constraints`, `mission_slas`

### Station Digital Twin (`models/station_twin.py`)
`station_capabilities`, `station_hardware`, `station_licenses`, `station_certifications`,
`station_certification_events`, `station_quality_scores`, `station_time_statuses`, `station_agent_identities`

### Contact Planning & Jobs (`models/contact.py`, `models/events.py`)
`visibility_opportunities`, `contact_opportunities`, `reservations`, `scheduled_contacts`,
`observation_jobs`, `execution_receipts`, `job_events`, `outbox_events`

## Relationship strategy

- `spacecraft` links back to the legacy `satellites` row (nullable FK) so existing NORAD data is reused.
- `visibility_opportunities.pass_prediction_id` (nullable FK) bridges the legacy `pass_predictions` table.
- New job chain replaces the old `Booking → Schedule → Operation` flow going forward, without dropping it.

## Rollback

`alembic downgrade base` (removes all). Legacy behavior is preserved up to the point of the
additive column changes; `ground_stations` new columns are nullable/defaulted so legacy inserts still work.