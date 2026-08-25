# Graph Report - afriGround  (2026-08-25)

## Corpus Check
- 237 files · ~186,869 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2212 nodes · 5070 edges · 145 communities (114 shown, 31 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 433 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4054e790`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- EdgeAgentService
- ObservationOrchestrator
- routes/data.py
- EarthScene.tsx
- StationService
- services/tenancy.py
- _post
- OperationsEngine
- ContactPlanningService
- simulate_edge.py
- agent.py
- RegulatoryAuthorizationService
- env.py
- test_api.py
- useT
- [locale]/page.tsx
- write_audit_log
- SLAService
- compilerOptions
- commercial_engine.py
- api.ts
- support.py
- TenantContext
- StationGatewayAdapter
- get_adapter
- celestrak.ts
- FastAPI
- keys.py
- commercial.py
- scripts
- Base
- AntennaController
- Implementation Plan: AfriGround GSaaS Platform (v2)
- devDependencies
- emit
- test_state_machine.py
- dependencies
- What You Must Do When Invoked
- AfriGround — Phase 1 → 4 Walkthrough
- booking/page.tsx
- 3. Normal Pass Workflow (Execute Many)
- RFController
- business.py
- What You Must Do When Invoked
- test_agent.py
- Config
- hal/__init__.py
- ReceiverController
- RecordingController
- mock_controllers.py
- interfaces.py
- gen_agent_certs.py
- CommercialEngine
- EdgeNodeFactory
- 2. Station Subsystems
- AfriGround AWS Deployment Plan (Phase 4.3)
- web/package.json
- layout.tsx
- PowerController
- routes/regulatory.py
- DeliveryService
- station/page.tsx
- MockModemController
- asyncio
- cinematic_landing_plan_final.md
- BackgroundWorker
- data/page.tsx
- [job_id]/page.tsx
- CinematicHero.tsx
- AGENTS.md
- CloudClient
- Settings
- graphify reference: extra exports and benchmark
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- PRODUCTION_SESSION_LOG — 2026-08-21
- next.config.ts
- graphify.js
- entrypoint.sh
- run.sh
- eslint.config.mjs
- next-intl
- postprocessing
- three
- @types/node
- postcss.config.mjs
- i18n.ts
- proxy.ts
- bootstrap_state.sh
- userdata.sh
- graphify reference: query, path, explain
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- Station Gateway Architecture
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- .agents/skills/graphify/references/extraction-spec.md
- .opencode/skills/graphify/references/extraction-spec.md
- Proposed Changes
- test_sla.py
- DATA_MODEL_MIGRATION_PLAN.md
- 14. Landing Page Narrative
- MockZodiacMCSAdapter
- 18. Implementation Phases
- Alternative 1: Schedule Injection Architecture
- AfriGround GSaaS Platform - System Capabilities Summary
- AFRIGROUND_ARCHITECTURE_AUDIT.md
- Frontend Integration Plan: Exposing Backend Features
- REGULATORY_RULES.md
- STATE_MACHINE_SPEC.md
- Walkthrough: Station Gateway Edge UI
- API_COMPATIBILITY_PLAN.md
- CERTIFICATION_WORKFLOW.md
- 9. Scene Contents
- CURRENT_FUNCTIONALITY.md — AfriGround (Pre-Migration Audit)
- web/README.md
- agent_client
- Settings
- AfriGround Station Gateway
- 1. Design Principles
- 20. Performance Requirements
- 3. AfriGround Visual Identity — "Orbital Infrastructure"
- web/AGENTS.md
- 2. Anti-Generic AI Design Rules
- 8. Cinematic Scene Concept
- AfriGround — Distinctive Cinematic Landing Page Implementation Plan

## God Nodes (most connected - your core abstractions)
1. `TenantContext` - 129 edges
2. `Base` - 76 edges
3. `ObservationOrchestrator` - 69 edges
4. `ObservationJob` - 66 edges
5. `_post()` - 63 edges
6. `ContactPlanningService` - 52 edges
7. `EdgeAgentService` - 46 edges
8. `RegulatoryAuthorizationService` - 45 edges
9. `GroundStation` - 40 edges
10. `StationService` - 40 edges

## Surprising Connections (you probably didn't know these)
- `test_agent_revoked_identity_rejected()` --uses--> `StationAgentIdentity`  [INFERRED]
  apps/api/tests/test_agent.py → apps/api/models/station_twin.py
- `get_current_user_db()` --uses--> `User`  [INFERRED]
  apps/api/auth.py → apps/api/models/core.py
- `EdgeNodeFactory` --uses--> `AntennaController`  [INFERRED]
  apps/api/hal/__init__.py → apps/api/hal/interfaces.py
- `EdgeNodeFactory` --uses--> `ModemController`  [INFERRED]
  apps/api/hal/__init__.py → apps/api/hal/interfaces.py
- `EdgeNodeFactory` --uses--> `PowerController`  [INFERRED]
  apps/api/hal/__init__.py → apps/api/hal/interfaces.py

## Import Cycles
- None detected.

## Communities (145 total, 31 thin omitted)

### Community 0 - "EdgeAgentService"
Cohesion: 0.06
Nodes (63): Incident, Per-agent heartbeat records used by the missed-heartbeat watchdog., Structured telemetry readings reported by station agents., Time synchronization quality reported by the station agent., StationHeartbeat, StationTelemetryReading, StationTimeStatus, acknowledge_job() (+55 more)

### Community 1 - "ObservationOrchestrator"
Cohesion: 0.07
Nodes (42): ObservationJob, Engineer's manual readiness confirmation for a job. Mandatory gate before…, Executable unit of work for the orchestrator / edge agent., StationReadinessEvent, JobEvent, State transition history for observation jobs (idempotent audit)., Saved, certified station configuration for a specific satellite mission.…, StationOperationProfile (+34 more)

### Community 2 - "routes/data.py"
Cohesion: 0.10
Nodes (27): decrypt_dict(), encrypt_dict(), Encrypts a dictionary into a Fernet token string., Decrypts a Fernet token string back into a dictionary., add_destination(), list_datasets(), list_destinations(), AsyncSession (+19 more)

### Community 3 - "EarthScene.tsx"
Cohesion: 0.07
Nodes (32): CinematicBackground(), EarthScene, SceneBoundary, Atmosphere(), Earth(), AFRICA_POLY, createEarthTexture(), drawRing() (+24 more)

### Community 4 - "StationService"
Cohesion: 0.13
Nodes (31): add_capability(), add_hardware(), add_license(), add_quality_score(), get_certification(), get_station(), list_agents(), list_capabilities() (+23 more)

### Community 5 - "services/tenancy.py"
Cohesion: 0.12
Nodes (34): Organization, Role, User, AuditLog, Permission, RolePermission, grant_permission(), list_audit_logs() (+26 more)

### Community 6 - "_post"
Cohesion: 0.12
Nodes (34): activate_mission(), create_constraint(), create_mission(), create_profile(), create_rf_profile(), create_sla(), create_spacecraft(), create_tc_command() (+26 more)

### Community 7 - "OperationsEngine"
Cohesion: 0.07
Nodes (45): MaintenanceEvent, network_ranking(), AsyncSession, get, create_incident(), create_maintenance(), evaluate_station_risk(), list_incidents() (+37 more)

### Community 8 - "ContactPlanningService"
Cohesion: 0.15
Nodes (15): Customer reservation against a contact opportunity., Reservation, GroundStation, ContactPlanningService, _now(), AsyncSession, datetime, UUID (+7 more)

### Community 9 - "simulate_edge.py"
Cohesion: 0.09
Nodes (52): DataDeliveryDestination, Mission, MissionProfile, MissionRFProfile, MissionSLA, MissionTelecommandDefinition, MissionTelemetryDefinition, SLA requirements attached to a mission. (+44 more)

### Community 10 - "agent.py"
Cohesion: 0.18
Nodes (23): acknowledge_job(), agent_heartbeat(), agent_telemetry(), agent_time_status(), assigned_jobs(), HeartbeatRequest, job_detail(), AsyncSession (+15 more)

### Community 11 - "RegulatoryAuthorizationService"
Cohesion: 0.13
Nodes (25): Edge agent identity for a station (mTLS bridge, Phase 4.0)., Current certification state of a station (Digital Twin lifecycle)., Auditable certification state transitions., StationAgentIdentity, StationCertification, StationCertificationEvent, _now(), AsyncSession (+17 more)

### Community 12 - "env.py"
Cohesion: 0.19
Nodes (13): do_run_migrations(), include_name(), include_object(), In this scenario we need to create an Engine and associate a connection with…, Run migrations in 'online' mode., Only manage application tables in the 'public' schema; never touch…, Filter removed tables from non-public schemas (include_object is not called for…, Run migrations in 'offline' mode. This configures the context with just a URL… (+5 more)

### Community 13 - "test_api.py"
Cohesion: 0.07
Nodes (23): authed_client(), client(), fixture, Route-level integration tests: real FastAPI app, real test DB, mocked Supabase…, A tenant without job.operate must get 403 on job endpoints., POST /api/v1/stations/{id}/tx requires station.manage; a tenant without…, TestClient with its own engine; connections are created inside the portal loop…, GET /api/v1/orchestration/metrics requires platform.admin. (+15 more)

### Community 14 - "useT"
Cohesion: 0.10
Nodes (21): ContractDashboard(), ContractData, MOCK_CONTRACT, CommercialQuotesPage(), LineItem, PRICING_TIERS, QuoteResult, ContactPage() (+13 more)

### Community 15 - "[locale]/page.tsx"
Cohesion: 0.12
Nodes (22): CountUp(), COAST, CoverageSection(), CoverageText, proj(), DataFlowText, DataFlowVisualization(), EarthIntelligence() (+14 more)

### Community 16 - "write_audit_log"
Cohesion: 0.09
Nodes (42): Idempotent per-webhook delivery record for a published outbox event (Phase 3.1)…, Webhook, WebhookDelivery, create_webhook(), delete_webhook(), list_webhooks(), AsyncSession, BaseModel (+34 more)

### Community 17 - "SLAService"
Cohesion: 0.22
Nodes (7): _now(), AsyncSession, datetime, UUID, SLA Enforcement (Phase 3.0) — evaluates mission SLAs when an observation job…, Evaluate all SLAs for the job's mission against its outcome. Creates an…, SLAService

### Community 18 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 19 - "commercial_engine.py"
Cohesion: 0.08
Nodes (37): Booking, PassPrediction, RecurringMission, Schedule, BookingService, AsyncSession, UUID, Transition a Pass Prediction into a REQUESTED Booking. Also runs compatibility… (+29 more)

### Community 20 - "api.ts"
Cohesion: 0.17
Nodes (26): dynamic, GET(), POST(), resolvePath(), STATION_CHILD_RE, LandingPage(), api(), apiGet() (+18 more)

### Community 21 - "support.py"
Cohesion: 0.15
Nodes (20): SupportTicket, create_ticket(), list_tickets(), AsyncSession, get, UUID, API Routes — Support Ticketing Engine, AsyncSession (+12 more)

### Community 22 - "TenantContext"
Cohesion: 0.20
Nodes (23): confirm_reservation(), create_contact_opportunities(), create_job(), create_reservation(), generate_visibility_opportunities(), get_job_details(), _job_dict(), list_job_events() (+15 more)

### Community 23 - "StationGatewayAdapter"
Cohesion: 0.15
Nodes (6): ABC, Returns ACU, HDR, Wind, Time status., Command the antenna to immediately stow to safe position., Immediately kill all RF transmissions., Abstract base class for interfacing with physical station hardware (MCS, ACU,…, StationGatewayAdapter

### Community 24 - "get_adapter"
Cohesion: 0.21
Nodes (12): get_adapter(), confirm_ready(), dashboard(), emergency_abort(), pass_console(), AsyncSession, get, Emergency abort — LOCAL-FIRST. Stops recording, kills TX, stows antenna. (+4 more)

### Community 25 - "celestrak.ts"
Cohesion: 0.15
Nodes (19): computePasses(), eciToEcf(), geodeticToEcf(), GET(), PassInfo, GET(), epochToUtc(), FALLBACK_TLES (+11 more)

### Community 26 - "FastAPI"
Cohesion: 0.07
Nodes (36): get_current_user(), get_current_user_db(), get_db_session(), AsyncSession, Verify the JWT token from Supabase., Extract user information from the verified token payload. In a real app, this…, Resolve the JWT subject to the persisted User row (Phase 1 tenancy)., verify_token() (+28 more)

### Community 27 - "keys.py"
Cohesion: 0.09
Nodes (40): APIKey, create_key(), key_me(), KeyCreateRequest, KeyCreateResponse, KeyListResponse, KeyMeResponse, list_keys() (+32 more)

### Community 28 - "commercial.py"
Cohesion: 0.17
Nodes (16): accept_quote(), create_contract(), create_quote(), create_recurring_mission(), get_contract_usage(), AsyncSession, get, UUID (+8 more)

### Community 29 - "scripts"
Cohesion: 0.10
Nodes (20): description, engines, node, pnpm, name, packageManager, private, scripts (+12 more)

### Community 30 - "Base"
Cohesion: 0.13
Nodes (28): Base, ContactOpportunity, A feasible RF contact opportunity for a mission profile on a specific pass., A confirmed, executable contact on the station schedule., Raw geometric pass: a spacecraft is geometrically visible from a station., ScheduledContact, VisibilityOpportunity, Quote (+20 more)

### Community 31 - "AntennaController"
Cohesion: 0.12
Nodes (9): AntennaController, AntennaPosition, BaseModel, Controls antenna pointing and tracking., Get the current antenna azimuth/elevation., Command the antenna to slew to a specific position., Begin auto-tracking a satellite using its TLE., Emergency stop / park the antenna. (+1 more)

### Community 32 - "Implementation Plan: AfriGround GSaaS Platform (v2)"
Cohesion: 0.05
Nodes (37): A. Current Architecture & Tech Stack, B. Current Database Schema & API Architecture, C. Existing Scheduling/Pass-Prediction Implementation, D. Existing Authentication/Authorization & Infrastructure, E. Missing GSaaS Components, F. Recommended Architectural Adjustments, G. Repository Changes Required, H. What Not To Do Yet (Phase 1 Guardrails) (+29 more)

### Community 33 - "devDependencies"
Cohesion: 0.11
Nodes (19): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/nodemailer, @types/react, @types/react-dom (+11 more)

### Community 34 - "emit"
Cohesion: 0.05
Nodes (75): Celery application for the AfriGround orchestration runtime (Phase 2.0). The…, OutboxEvent, Transactional outbox: durable events emitted with their owning transaction., drain_once(), main(), Orchestration runtime dispatcher — polls the outbox, publishes due events, and…, _request_stop(), run() (+67 more)

### Community 35 - "test_state_machine.py"
Cohesion: 0.14
Nodes (3): State Machine — shared transition maps and validation for Phase 1 domain…, Validates and applies state transitions from a declarative map., StateMachine

### Community 36 - "dependencies"
Cohesion: 0.12
Nodes (17): dependencies, next, nodemailer, react, react-dom, @react-three/drei, @react-three/fiber, @react-three/postprocessing (+9 more)

### Community 37 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 38 - "AfriGround — Phase 1 → 4 Walkthrough"
Cohesion: 0.06
Nodes (34): 1.0 Audit & preservation, 1.1 Tenancy & RBAC, 1.2 Mission & spacecraft model, 1.3 Station digital twin & certification, 1.4 Contact planning & job state machine, 1.5 Safety & regulatory enforcement, 1.6–1.8 API contracts, seeds, outbox consumer, tests, 2.0 Orchestration runtime (+26 more)

### Community 39 - "booking/page.tsx"
Cohesion: 0.17
Nodes (11): BookingWizard(), PassesResponse, PassInfo, Quote, SatSearch, SatSearchResponse, SIM_FALLBACK_PASSES, SupportPortal() (+3 more)

### Community 40 - "3. Normal Pass Workflow (Execute Many)"
Cohesion: 0.07
Nodes (28): 1.1 Station Registration (Cloud Side), 1.2 Edge Agent Installation (Station Side), 1.3 Capability Registration, 1.4 Integration Testing, 1.5 Station Certification, 1. Station Registration & Installation, 2.1 Mission Profile Arrives, 2.2 Station Engineer Configures Equipment (+20 more)

### Community 41 - "RFController"
Cohesion: 0.18
Nodes (4): Controls RF chain configuration., RFController, RFStatus, MockRFController

### Community 42 - "business.py"
Cohesion: 0.23
Nodes (13): contract_usage(), ContractUsageResponse, AsyncSession, BaseModel, get, UUID, API Routes — Business tier (Phase 3.0): SLA violations, contract usage,…, Manually run the recurring-mission booking sweep for the org (the Celery beat… (+5 more)

### Community 43 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 44 - "test_agent.py"
Cohesion: 0.11
Nodes (26): ExecutionReceipt, Post-execution result report for an observation job. Generated by the Edge…, AgentDispatchService, _now(), AsyncSession, BaseModel, datetime, ExecutionReceipt (+18 more)

### Community 45 - "Config"
Cohesion: 0.41
Nodes (6): Config, CachedJob, CachedProfile, get_db(), init_db(), lifespan()

### Community 46 - "hal/__init__.py"
Cohesion: 0.22
Nodes (4): HAL — Hardware Abstraction Layer package. Provides a factory to get controller…, Controls the transmitter for uplink/TT&C., TransmitterController, MockTransmitterController

### Community 47 - "ReceiverController"
Cohesion: 0.18
Nodes (4): Controls the receiver/demodulator., Returns SNR, BER, Eb/N0 etc., ReceiverController, MockReceiverController

### Community 48 - "RecordingController"
Cohesion: 0.24
Nodes (4): Controls data recording to disk., RecordingController, RecordingStatus, MockRecordingController

### Community 49 - "mock_controllers.py"
Cohesion: 0.26
Nodes (6): Reads weather station data for risk assessment., Returns True if weather conditions permit antenna operations., WeatherController, WeatherData, MockWeatherController, Hardware Abstraction Layer — Mock implementations for development and testing.…

### Community 50 - "interfaces.py"
Cohesion: 0.20
Nodes (7): ModemController, ABC, Any, Hardware Abstraction Layer (HAL) — Interfaces for Ground Station Edge…, Controls the modem for data encoding/decoding., Returns frame count, error rate, throughput., Get comprehensive antenna status.

### Community 51 - "gen_agent_certs.py"
Cohesion: 0.36
Nodes (11): build_agent(), build_ca(), build_server(), _key(), main(), Phase 4.0 — Dev mTLS certificate bootstrap for the edge agent bridge. Generates…, _write_cert(), _write_key() (+3 more)

### Community 52 - "CommercialEngine"
Cohesion: 0.14
Nodes (12): Contract, CommercialEngine, ContractResponse, AsyncSession, UUID, QuoteResponse, Generate a price quote for one or more bookings. Calculates cost based on…, Customer accepts a quote — transitions bookings to RESERVED. (+4 more)

### Community 53 - "EdgeNodeFactory"
Cohesion: 0.24
Nodes (6): EdgeNodeFactory, Factory for creating hardware controller instances. In development, returns…, Controls Software Defined Radio equipment., Returns spectrum analysis data., SDRController, MockSDRController

### Community 54 - "2. Station Subsystems"
Cohesion: 0.08
Nodes (23): 1. Station Overview, 2.1 Antenna, 2.2 Antenna Control Unit (ACU), 2.3 Antenna Drive Unit (ADU), 2.4 CORTEX HDR (High Data Rate Receiver), 2.5 CORTEX CRT (TT&C Unit), 2.6 CORTEX DTR (Digital Tracking Receiver), 2.7 Mission Control Software (MCS) (+15 more)

### Community 55 - "AfriGround AWS Deployment Plan (Phase 4.3)"
Cohesion: 0.11
Nodes (17): 1. Authenticate, 2. Bootstrap remote state (one-time), 3. Init + plan, 4. Apply, 5. Push images to ECR, 6. Deploy the web app, 7. Verify, AfriGround AWS Deployment Plan (Phase 4.3) (+9 more)

### Community 56 - "web/package.json"
Cohesion: 0.20
Nodes (9): name, packageManager, private, scripts, build, dev, lint, start (+1 more)

### Community 57 - "layout.tsx"
Cohesion: 0.24
Nodes (4): ibmPlexMono, spaceGrotesk, Footer(), Navbar()

### Community 58 - "PowerController"
Cohesion: 0.31
Nodes (4): PowerController, PowerStatus, Monitors and controls power systems., MockPowerController

### Community 59 - "routes/regulatory.py"
Cohesion: 0.44
Nodes (8): agent_heartbeat(), evaluate_tx(), AsyncSession, UUID, API Routes — Regulatory Enforcement (Phase 1.5), register_station(), report_time_status(), transition_certification()

### Community 60 - "DeliveryService"
Cohesion: 0.17
Nodes (19): DataDeliveryJob, Dataset, _checksum(), DeliveryService, _now(), AsyncSession, datetime, UUID (+11 more)

### Community 61 - "station/page.tsx"
Cohesion: 0.22
Nodes (6): StationHealthDashboard(), StationRisk, TelemetryData, Agent, Station, TimeStatus

### Community 63 - "asyncio"
Cohesion: 0.46
Nodes (7): _alembic_config(), Guard against the tiger/topology regression: the migration must never emit DROP…, _run_upgrade_head(), test_migration_applies_cleanly(), test_migration_is_idempotent(), test_no_extension_schema_drops(), asyncio

### Community 64 - "cinematic_landing_plan_final.md"
Cohesion: 0.11
Nodes (17): 10. Orbital Motion, 11. Ground-to-Satellite Link, 12. Technical HUD, 13. Hero Copy, 15. Layout System, 16. Motion System, 17. File Structure, 19. Visual QA Prompt for Antigravity / OpenCode (+9 more)

### Community 66 - "data/page.tsx"
Cohesion: 0.40
Nodes (5): DataCatalog(), DatasetRow, mapDataset(), MOCK_DATASETS, Dataset

### Community 67 - "[job_id]/page.tsx"
Cohesion: 0.33
Nodes (4): ExecutionReceipt, JobDetails, JobDetailsPage(), ReadinessEvent

### Community 68 - "CinematicHero.tsx"
Cohesion: 0.47
Nodes (4): AfriGroundTechnicalHUD(), HudText, CinematicHero(), HeroText

### Community 69 - "AGENTS.md"
Cohesion: 0.13
Nodes (14): CURRENT REPOSITORY STATE, FINAL INSTRUCTIONS, graphify, ROLE AND CONTEXT, STEP 1: Upgrade Cloud Database Models, STEP 2: Create the Station Gateway App Skeleton, STEP 3: Implement the Station Gateway Adapter Pattern, STEP 4: Build the Local Operator Console (Edge UI) (+6 more)

### Community 81 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 82 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 83 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 84 - "PRODUCTION_SESSION_LOG — 2026-08-21"
Cohesion: 0.12
Nodes (16): 1. Session goals, 2.1 Hydration error #418 — FIXED, DEPLOYED, VERIFIED, 2.2 Secrets hygiene — all credentials moved to environment variables, 2.3 Demo data enrichment — live feeds now look real, 2.4 JWT secret rotation, 2. What was done, 3. Operational runbooks, 4. Current live architecture (+8 more)

### Community 102 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 103 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 104 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 105 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 106 - "Station Gateway Architecture"
Cohesion: 0.12
Nodes (15): 1. Purpose, 2. Application Structure, 3. Adapter Interface, 4. Cloud Communication, 5. Local Operator Console, 6. Security Model, Abstract Methods, Dashboard (+7 more)

### Community 107 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 108 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 109 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 116 - "Proposed Changes"
Cohesion: 0.13
Nodes (14): 1. Cloud Client Extensions, 2. Background Workers, 3. FastAPI Integration, 4. Runner Script & Documentation, Automated Tests, Manual Verification, [MODIFY] [cloud_client.py](file:///c:/Users/melam/Documents/dev/gsas/afriGround/apps/station-gateway/cloud_client.py), [MODIFY] [main.py](file:///c:/Users/melam/Documents/dev/gsas/afriGround/apps/station-gateway/main.py) (+6 more)

### Community 117 - "test_sla.py"
Cohesion: 0.32
Nodes (11): _add_sla(), _make_job(), Phase 3.0 tests — SLA enforcement on job completion, contract usage., SystemJobDriver terminal transitions trigger enforcement automatically., A COMPLETED job whose wall-clock processing time exceeds the delay., _slow_job(), test_contract_usage_aggregates_completed_jobs(), test_runtime_enforces_sla_on_terminal_transition() (+3 more)

### Community 118 - "DATA_MODEL_MIGRATION_PLAN.md"
Cohesion: 0.17
Nodes (10): Contact Planning & Jobs (`models/contact.py`, `models/events.py`), Legacy tables — kept unchanged, Mission & Spacecraft (`models/mission.py`), Modified tables (additive columns), New Phase 1 tables, Principles, Relationship strategy, Rollback (+2 more)

### Community 119 - "14. Landing Page Narrative"
Cohesion: 0.18
Nodes (11): 14. Landing Page Narrative, Section 01 — HERO, Section 02 — NETWORK, Section 03 — GROUND INFRASTRUCTURE, Section 04 — MISSION CONTROL, Section 05 — DATA, Section 06 — EARTH INTELLIGENCE, Section 07 — ENGINEERING (+3 more)

### Community 121 - "18. Implementation Phases"
Cohesion: 0.20
Nodes (10): 18. Implementation Phases, Phase 0 — Design System First, Phase 1 — Scaffold, Phase 2 — Static Scene, Phase 3 — Satellite + Orbit, Phase 4 — Ground Station + Link, Phase 5 — Technical HUD, Phase 6 — Cinematic Polish (+2 more)

### Community 122 - "Alternative 1: Schedule Injection Architecture"
Cohesion: 0.25
Nodes (7): 1. Cloud API Updates (`apps/api`), 2. Edge Agent Updates (`apps/station-gateway`), 3. Transition Strategy, Alternative 1: Schedule Injection Architecture, Core Principles, Implementation Steps, Overview

### Community 123 - "AfriGround GSaaS Platform - System Capabilities Summary"
Cohesion: 0.25
Nodes (7): 1. Core Mission & Architecture, 2. Backend Capabilities (`apps/api`), 3. Frontend Capabilities (`apps/web`), 4. Edge Agent (`apps/station-gateway`), 5. Testing & DevOps, 6. Known Gaps / Next Steps, AfriGround GSaaS Platform - System Capabilities Summary

### Community 124 - "AFRIGROUND_ARCHITECTURE_AUDIT.md"
Cohesion: 0.29
Nodes (5): Gaps vs. GSaaS OS target, Guardrails (must not break), Recommended adjustments (implemented in Phase 1), Stack, Strengths

### Community 125 - "Frontend Integration Plan: Exposing Backend Features"
Cohesion: 0.29
Nodes (6): 1. Goal, 2. API Updates (`apps/api`), 3.1 Job Details Page, 3.2 Navigation Hooks, 3. Frontend Updates (`apps/web`), Frontend Integration Plan: Exposing Backend Features

### Community 126 - "REGULATORY_RULES.md"
Cohesion: 0.29
Nodes (5): Audit, Geographic / coordination notes, Implementation, Safety defaults, TX authorization checks (all must pass)

### Community 127 - "STATE_MACHINE_SPEC.md"
Cohesion: 0.29
Nodes (5): Certification workflow (StationCertification), ContactOpportunity lifecycle, Incident lifecycle (legacy, kept), ObservationJob lifecycle, Reservation lifecycle

### Community 128 - "Walkthrough: Station Gateway Edge UI"
Cohesion: 0.29
Nodes (6): 🖥️ 1. Edge Operator Console (`apps/station-gateway/templates/`), 🛑 2. The Readiness Gate (Safety Interlock), 🚨 3. Local-First Emergency Abort, 📄 4. Post-Pass Execution Receipts, 📚 5. User Guide Expanded, Walkthrough: Station Gateway Edge UI

### Community 129 - "API_COMPATIBILITY_PLAN.md"
Cohesion: 0.33
Nodes (4): Compatibility guarantees, Deployment notes, Goal, Tenant scoping

### Community 130 - "CERTIFICATION_WORKFLOW.md"
Cohesion: 0.33
Nodes (4): Enforced invariants, Flow, Implementation, States

### Community 131 - "9. Scene Contents"
Cohesion: 0.33
Nodes (6): 9.1 Starfield, 9.2 Earth, 9.3 Atmosphere, 9.4 Ground Station, 9.5 Satellite, 9. Scene Contents

### Community 132 - "CURRENT_FUNCTIONALITY.md — AfriGround (Pre-Migration Audit)"
Cohesion: 0.33
Nodes (5): API Surface (current), Behavior notes, CURRENT_FUNCTIONALITY.md — AfriGround (Pre-Migration Audit), Domain models (current tables), Scope

### Community 133 - "web/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 134 - "agent_client"
Cohesion: 0.67
Nodes (3): agent_client(), fixture, TestClient over the real app; agent identity/chain pre-seeded in the DB.

### Community 137 - "1. Design Principles"
Cohesion: 0.67
Nodes (3): 1.1 Primary Design Objective, 1.2 Design Personality, 1. Design Principles

### Community 138 - "20. Performance Requirements"
Cohesion: 0.67
Nodes (3): 20. Performance Requirements, Desktop, Mobile

### Community 139 - "3. AfriGround Visual Identity — "Orbital Infrastructure""
Cohesion: 0.67
Nodes (3): 3.1 Color Direction, 3.2 Typography, 3. AfriGround Visual Identity — "Orbital Infrastructure"

## Knowledge Gaps
- **493 isolated node(s):** `entrypoint.sh script`, `run.sh script`, `eslintConfig`, `withNextIntl`, `nextConfig` (+488 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TenantContext` connect `TenantContext` to `EdgeAgentService`, `ObservationOrchestrator`, `StationService`, `services/tenancy.py`, `_post`, `OperationsEngine`, `ContactPlanningService`, `routes/regulatory.py`, `business.py`, `simulate_edge.py`, `RegulatoryAuthorizationService`, `test_api.py`, `write_audit_log`, `FastAPI`, `keys.py`, `Base`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `ObservationJob` connect `ObservationOrchestrator` to `EdgeAgentService`, `emit`, `simulate_edge.py`, `test_agent.py`, `SLAService`, `commercial_engine.py`, `CommercialEngine`, `TenantContext`, `DeliveryService`, `Base`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `Base` connect `Base` to `EdgeAgentService`, `ObservationOrchestrator`, `emit`, `services/tenancy.py`, `OperationsEngine`, `ContactPlanningService`, `simulate_edge.py`, `RegulatoryAuthorizationService`, `env.py`, `test_agent.py`, `Config`, `write_audit_log`, `commercial_engine.py`, `CommercialEngine`, `support.py`, `keys.py`, `DeliveryService`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `TenantContext` (e.g. with `Organization` and `Role`) actually correct?**
  _`TenantContext` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ObservationOrchestrator` (e.g. with `create_job()` and `list_job_events()`) actually correct?**
  _`ObservationOrchestrator` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `ObservationJob` (e.g. with `get_job_details()` and `_job_dict()`) actually correct?**
  _`ObservationJob` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `entrypoint.sh script`, `run.sh script`, `eslintConfig` to the rest of the system?**
  _493 weakly-connected nodes found - possible documentation gaps or missing edges._