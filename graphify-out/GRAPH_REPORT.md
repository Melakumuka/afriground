# Graph Report - afriGround  (2026-08-25)

## Corpus Check
- 239 files · ~191,507 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2291 nodes · 5154 edges · 156 communities (121 shown, 35 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 445 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1ba32260`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- EdgeAgentService
- ObservationOrchestrator
- routes/data.py
- EarthScene.tsx
- StationService
- FastAPI
- MissionService
- OperationsEngine
- ContactPlanningService
- simulate_edge.py
- readiness.py
- RegulatoryAuthorizationService
- asyncio
- test_api.py
- useT
- [locale]/page.tsx
- test_webhooks.py
- test_sla.py
- compilerOptions
- booking_service.py
- api.ts
- api/main.py
- TenantContext
- StationGatewayAdapter
- operator.py
- celestrak.ts
- orchestration_runtime.py
- keys.py
- commercial_engine.py
- scripts
- Base
- AntennaController
- Implementation Plan: AfriGround GSaaS Platform (v2)
- devDependencies
- test_orchestration_runtime.py
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
- local_db.py
- hal/__init__.py
- ReceiverController
- RecordingController
- mock_controllers.py
- interfaces.py
- gen_agent_certs.py
- SGP4Engine
- EdgeNodeFactory
- 2. Station Subsystems
- AfriGround AWS Deployment Plan (Phase 4.3)
- web/package.json
- layout.tsx
- PowerController
- RecurringMissionSweeper
- DeliveryService
- station/page.tsx
- MockModemController
- IsolatedObserver
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
- events.py
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
- OutboxEvent
- BaseSettings
- AfriGround Station Gateway
- 1. Design Principles
- 20. Performance Requirements
- 3. AfriGround Visual Identity — "Orbital Infrastructure"
- web/AGENTS.md
- 2. Anti-Generic AI Design Rules
- 8. Cinematic Scene Concept
- AfriGround — Distinctive Cinematic Landing Page Implementation Plan
- tasks.py
- publish_pending
- test_delivery.py
- outbox_worker.py
- opencode.json
- datetime
- ExecutionReceipt
- HTTPException
- UUID
- ABC
- get

## God Nodes (most connected - your core abstractions)
1. `TenantContext` - 127 edges
2. `Base` - 74 edges
3. `ObservationOrchestrator` - 64 edges
4. `_post()` - 61 edges
5. `ContactPlanningService` - 52 edges
6. `EdgeAgentService` - 46 edges
7. `ObservationJob` - 45 edges
8. `RegulatoryAuthorizationService` - 45 edges
9. `StationService` - 40 edges
10. `GroundStation` - 40 edges

## Surprising Connections (you probably didn't know these)
- `create_job()` --uses--> `ObservationOrchestrator`  [INFERRED]
  apps/api/routes/contact.py → apps/api/services/orchestrator.py
- `list_job_events()` --uses--> `ObservationOrchestrator`  [INFERRED]
  apps/api/routes/contact.py → apps/api/services/orchestrator.py
- `list_jobs()` --uses--> `ObservationOrchestrator`  [INFERRED]
  apps/api/routes/contact.py → apps/api/services/orchestrator.py
- `record_receipt()` --uses--> `ObservationOrchestrator`  [INFERRED]
  apps/api/routes/contact.py → apps/api/services/orchestrator.py
- `transition_job()` --uses--> `ObservationOrchestrator`  [INFERRED]
  apps/api/routes/contact.py → apps/api/services/orchestrator.py

## Import Cycles
- None detected.

## Communities (156 total, 35 thin omitted)

### Community 0 - "EdgeAgentService"
Cohesion: 0.05
Nodes (81): Incident, Structured telemetry readings reported by station agents., StationTelemetryReading, acknowledge_job(), agent_heartbeat(), agent_telemetry(), agent_time_status(), assigned_jobs() (+73 more)

### Community 1 - "ObservationOrchestrator"
Cohesion: 0.19
Nodes (9): JobNotFound, ObservationOrchestrator, AsyncSession, ExecutionReceipt, HTTPException, JobEvent, ObservationJob, TenantContext (+1 more)

### Community 2 - "routes/data.py"
Cohesion: 0.10
Nodes (27): decrypt_dict(), encrypt_dict(), Encrypts a dictionary into a Fernet token string., Decrypts a Fernet token string back into a dictionary., add_destination(), list_datasets(), list_destinations(), AsyncSession (+19 more)

### Community 3 - "EarthScene.tsx"
Cohesion: 0.07
Nodes (32): CinematicBackground(), EarthScene, SceneBoundary, Atmosphere(), Earth(), AFRICA_POLY, createEarthTexture(), drawRing() (+24 more)

### Community 4 - "StationService"
Cohesion: 0.13
Nodes (31): add_capability(), add_hardware(), add_license(), add_quality_score(), get_certification(), get_station(), list_agents(), list_capabilities() (+23 more)

### Community 5 - "FastAPI"
Cohesion: 0.07
Nodes (44): get_current_user_db(), get_db_session(), AsyncSession, Verify the JWT token from Supabase., Resolve the JWT subject to the persisted User row (Phase 1 tenancy)., verify_token(), AuditLog, grant_permission() (+36 more)

### Community 6 - "MissionService"
Cohesion: 0.11
Nodes (33): activate_mission(), create_constraint(), create_mission(), create_profile(), create_rf_profile(), create_sla(), create_spacecraft(), create_tc_command() (+25 more)

### Community 7 - "OperationsEngine"
Cohesion: 0.06
Nodes (56): MaintenanceEvent, Per-agent heartbeat records used by the missed-heartbeat watchdog., Periodic quality scoring for a station (feeds routing/risk)., StationHeartbeat, StationQualityScore, network_ranking(), AsyncSession, get (+48 more)

### Community 8 - "ContactPlanningService"
Cohesion: 0.13
Nodes (25): ContactOpportunity, A feasible RF contact opportunity for a mission profile on a specific pass., Customer reservation against a contact opportunity., A confirmed, executable contact on the station schedule., Raw geometric pass: a spacecraft is geometrically visible from a station., Reservation, ScheduledContact, VisibilityOpportunity (+17 more)

### Community 9 - "simulate_edge.py"
Cohesion: 0.09
Nodes (49): Mission, MissionProfile, MissionRFProfile, MissionSLA, MissionTelecommandDefinition, MissionTelemetryDefinition, SLA requirements attached to a mission., Operational campaign against a spacecraft. (+41 more)

### Community 10 - "readiness.py"
Cohesion: 0.16
Nodes (17): Engineer's manual readiness confirmation for a job. Mandatory gate before…, StationReadinessEvent, Saved, certified station configuration for a specific satellite mission.…, StationOperationProfile, _now(), AsyncSession, datetime, HTTPException (+9 more)

### Community 11 - "RegulatoryAuthorizationService"
Cohesion: 0.14
Nodes (24): Regulatory license held by the station operator., Current certification state of a station (Digital Twin lifecycle)., Auditable certification state transitions., StationCertification, StationCertificationEvent, StationLicense, _now(), BaseModel (+16 more)

### Community 12 - "asyncio"
Cohesion: 0.13
Nodes (20): do_run_migrations(), include_name(), include_object(), In this scenario we need to create an Engine and associate a connection with…, Run migrations in 'online' mode., Only manage application tables in the 'public' schema; never touch…, Filter removed tables from non-public schemas (include_object is not called for…, Run migrations in 'offline' mode. This configures the context with just a URL… (+12 more)

### Community 13 - "test_api.py"
Cohesion: 0.07
Nodes (23): authed_client(), client(), fixture, Route-level integration tests: real FastAPI app, real test DB, mocked Supabase…, A tenant without job.operate must get 403 on job endpoints., POST /api/v1/stations/{id}/tx requires station.manage; a tenant without…, TestClient with its own engine; connections are created inside the portal loop…, GET /api/v1/orchestration/metrics requires platform.admin. (+15 more)

### Community 14 - "useT"
Cohesion: 0.10
Nodes (21): ContractDashboard(), ContractData, MOCK_CONTRACT, CommercialQuotesPage(), LineItem, PRICING_TIERS, QuoteResult, ContactPage() (+13 more)

### Community 15 - "[locale]/page.tsx"
Cohesion: 0.12
Nodes (22): CountUp(), COAST, CoverageSection(), CoverageText, proj(), DataFlowText, DataFlowVisualization(), EarthIntelligence() (+14 more)

### Community 16 - "test_webhooks.py"
Cohesion: 0.14
Nodes (27): Idempotent per-webhook delivery record for a published outbox event (Phase 3.1)…, Webhook, WebhookDelivery, _backoff(), _deliver_one(), deliver_org_webhooks(), _json_dumps(), _matches() (+19 more)

### Community 17 - "test_sla.py"
Cohesion: 0.14
Nodes (20): Recorded SLA breach (Phase 3.0) — created by the runtime on job completion., SLASLAViolation, _now(), AsyncSession, datetime, UUID, SLA Enforcement (Phase 3.0) — evaluates mission SLAs when an observation job…, Evaluate all SLAs for the job's mission against its outcome. Creates an… (+12 more)

### Community 18 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 19 - "booking_service.py"
Cohesion: 0.19
Nodes (14): BookingService, AsyncSession, UUID, Transition a Pass Prediction into a REQUESTED Booking. Also runs compatibility…, Transition a Booking to CONFIRMED and its Schedule to SCHEDULED., CompatibilityEngine, CompatibilityResult, GroundStationCapabilities (+6 more)

### Community 20 - "api.ts"
Cohesion: 0.17
Nodes (26): dynamic, GET(), POST(), resolvePath(), STATION_CHILD_RE, LandingPage(), api(), apiGet() (+18 more)

### Community 21 - "api/main.py"
Cohesion: 0.06
Nodes (42): get_current_user(), Extract user information from the verified token payload. In a real app, this…, health_check(), healthz_check(), AsyncSession, get, Stamp request state with the verified JWT subject (tenant resolution happens in…, Liveness probe (Phase 3.3): verifies DB reachability. 503 when down. (+34 more)

### Community 22 - "TenantContext"
Cohesion: 0.15
Nodes (33): Manually run the recurring-mission booking sweep for the org (the Celery beat…, trigger_recurring_booking(), confirm_reservation(), create_contact_opportunities(), create_job(), create_reservation(), generate_visibility_opportunities(), get_job_details() (+25 more)

### Community 23 - "StationGatewayAdapter"
Cohesion: 0.08
Nodes (12): ABC, Command the antenna to immediately stow to safe position. NOTE: per the…, Immediately kill all RF transmissions. NOTE: per the Isolated Observer Profile,…, Abstract base class for interfacing with physical station hardware (MCS, ACU,…, Returns the extended Safran health snapshot used by the dashboard:…, Subscribe to RM Port 4000. Real adapter: open a TCP socket to…, FTP pull of the MCS activity table. Returns the file content (XML)., FTP pull of completed pass XML reports from D:\\MCS_PUBLIC\\Pass. (+4 more)

### Community 24 - "operator.py"
Cohesion: 0.14
Nodes (26): CachedJob, CachedProfile, FirewallAuditLog, LocalActionAck, Per-rule firewall posture audit. Local-first; never assumes cloud., Engineer acknowledgement of the passive / no-active-commands notice., confirm_ready(), dashboard() (+18 more)

### Community 25 - "celestrak.ts"
Cohesion: 0.15
Nodes (19): computePasses(), eciToEcf(), geodeticToEcf(), GET(), PassInfo, GET(), epochToUtc(), FALLBACK_TLES (+11 more)

### Community 26 - "orchestration_runtime.py"
Cohesion: 0.18
Nodes (11): orchestration_metrics(), AsyncSession, get, API Routes — Orchestration Runtime (Phase 2.0): outbox health/backpressure., metrics(), _now(), AsyncSession, datetime (+3 more)

### Community 27 - "keys.py"
Cohesion: 0.09
Nodes (40): APIKey, create_key(), key_me(), KeyCreateRequest, KeyCreateResponse, KeyListResponse, KeyMeResponse, list_keys() (+32 more)

### Community 28 - "commercial_engine.py"
Cohesion: 0.10
Nodes (28): accept_quote(), create_contract(), create_quote(), create_recurring_mission(), get_contract_usage(), AsyncSession, get, UUID (+20 more)

### Community 29 - "scripts"
Cohesion: 0.10
Nodes (20): description, engines, node, pnpm, name, packageManager, private, scripts (+12 more)

### Community 30 - "Base"
Cohesion: 0.16
Nodes (27): Base, Organization, Quote, Role, User, Operation, Constellation, ConstellationSatellite (+19 more)

### Community 31 - "AntennaController"
Cohesion: 0.12
Nodes (9): AntennaController, AntennaPosition, BaseModel, Controls antenna pointing and tracking., Get the current antenna azimuth/elevation., Command the antenna to slew to a specific position., Begin auto-tracking a satellite using its TLE., Emergency stop / park the antenna. (+1 more)

### Community 32 - "Implementation Plan: AfriGround GSaaS Platform (v2)"
Cohesion: 0.05
Nodes (37): A. Current Architecture & Tech Stack, B. Current Database Schema & API Architecture, C. Existing Scheduling/Pass-Prediction Implementation, D. Existing Authentication/Authorization & Infrastructure, E. Missing GSaaS Components, F. Recommended Architectural Adjustments, G. Repository Changes Required, H. What Not To Do Yet (Phase 1 Guardrails) (+29 more)

### Community 33 - "devDependencies"
Cohesion: 0.11
Nodes (19): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/nodemailer, @types/react, @types/react-dom (+11 more)

### Community 34 - "test_orchestration_runtime.py"
Cohesion: 0.17
Nodes (19): process_observation_events(), Consume PUBLISHED OBSERVATION_JOB.* events. In simulate mode the runtime stands…, backoff_seconds(), Exponential backoff capped at RETRY_MAX_S: base * 2**(attempt-1)., _emit(), Phase 2.0 orchestration runtime tests: outbox retry/backoff, simulated job…, A hook that stops failing lets the retried event publish., _register_hook() (+11 more)

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
Cohesion: 0.26
Nodes (12): Contract, contract_usage(), ContractUsageResponse, AsyncSession, BaseModel, get, UUID, API Routes — Business tier (Phase 3.0): SLA violations, contract usage,… (+4 more)

### Community 43 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 44 - "test_agent.py"
Cohesion: 0.08
Nodes (38): ExecutionReceipt, ObservationJob, Executable unit of work for the orchestrator / edge agent., Post-execution result report for an observation job. Generated by the Edge…, Edge agent identity for a station (mTLS bridge, Phase 4.0)., StationAgentIdentity, get_agent_identity(), AsyncSession (+30 more)

### Community 45 - "local_db.py"
Cohesion: 0.28
Nodes (7): CRTRedundancyLog, get_db(), init_db(), LCBEngagementLog, Local Control Box (hand-paddle) engagement log., CRT (S/N 19019) redundancy state log., lifespan()

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

### Community 52 - "SGP4Engine"
Cohesion: 0.15
Nodes (9): AsyncSession, AsyncSession, PassResult, BaseModel, datetime, Predict satellite passes over a specific ground station within a time window., SGP4Engine, EarthSatellite (+1 more)

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

### Community 59 - "RecurringMissionSweeper"
Cohesion: 0.18
Nodes (14): Booking, PassPrediction, RecurringMission, Schedule, Auto-generates bookings for active recurring missions from TLE pass…, RecurringMissionSweeper, AsyncSession, datetime (+6 more)

### Community 60 - "DeliveryService"
Cohesion: 0.20
Nodes (13): DataDeliveryDestination, DataDeliveryJob, Dataset, _checksum(), DeliveryService, _now(), AsyncSession, datetime (+5 more)

### Community 61 - "station/page.tsx"
Cohesion: 0.22
Nodes (6): StationHealthDashboard(), StationRisk, TelemetryData, Agent, Station, TimeStatus

### Community 63 - "IsolatedObserver"
Cohesion: 0.11
Nodes (8): IsolatedObserver, Read-only Safran Pro 730 SX health/status aggregator. Never issues a command to…, RM 4000 ping + last packet age., Inferred from ACU RM stream., Inferred from ACU RM stream., Safran PC Saphir D: occupancy percent, Nominal vs Spare vs SPOF, Interpass + rise-angle conflicts

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

### Community 79 - "CloudClient"
Cohesion: 0.13
Nodes (6): get_adapter(), CloudClient, Config, Settings, ExecutionService, BaseSettings

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

### Community 117 - "events.py"
Cohesion: 0.15
Nodes (13): JobEvent, State transition history for observation jobs (idempotent audit)., _now(), Observation Orchestrator — drives ObservationJob lifecycle with a strict state…, test_create_job(), test_duplicate_job_rejected(), test_invalid_transition_rejected(), test_job_full_lifecycle() (+5 more)

### Community 118 - "DATA_MODEL_MIGRATION_PLAN.md"
Cohesion: 0.17
Nodes (10): Contact Planning & Jobs (`models/contact.py`, `models/events.py`), Legacy tables — kept unchanged, Mission & Spacecraft (`models/mission.py`), Modified tables (additive columns), New Phase 1 tables, Principles, Relationship strategy, Rollback (+2 more)

### Community 119 - "14. Landing Page Narrative"
Cohesion: 0.18
Nodes (11): 14. Landing Page Narrative, Section 01 — HERO, Section 02 — NETWORK, Section 03 — GROUND INFRASTRUCTURE, Section 04 — MISSION CONTROL, Section 05 — DATA, Section 06 — EARTH INTELLIGENCE, Section 07 — ENGINEERING (+3 more)

### Community 120 - "MockZodiacMCSAdapter"
Cohesion: 0.09
Nodes (7): MockZodiacMCSAdapter, Mock activity table XML., Mock list of completed-pass report XML files., Mock implementation of the Safran Pro 730 SX / Zodiac PFM730 MCS adapter.…, Test helper: set CRT state to 'nominal' | 'spare' | 'spof'., Extended Safran health snapshot for the dashboard., Mock RM Port 4000 stream — yields one Az/El sample.

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

### Community 134 - "OutboxEvent"
Cohesion: 0.23
Nodes (14): OutboxEvent, Transactional outbox: durable events emitted with their owning transaction., dispatch_job_to_webhook(), dispatch_receipt_to_webhook(), dispatch_station_to_webhook(), _json_dumps(), _post_webhook(), Publish hooks for the transactional outbox — concrete consumers registered… (+6 more)

### Community 137 - "1. Design Principles"
Cohesion: 0.67
Nodes (3): 1.1 Primary Design Objective, 1.2 Design Personality, 1. Design Principles

### Community 138 - "20. Performance Requirements"
Cohesion: 0.67
Nodes (3): 20. Performance Requirements, Desktop, Mobile

### Community 139 - "3. AfriGround Visual Identity — "Orbital Infrastructure""
Cohesion: 0.67
Nodes (3): 3.1 Color Direction, 3.2 Typography, 3. AfriGround Visual Identity — "Orbital Infrastructure"

### Community 145 - "tasks.py"
Cohesion: 0.26
Nodes (12): Celery application for the AfriGround orchestration runtime (Phase 2.0). The…, check_heartbeats(), drain_outbox(), outbox_metrics(), Celery tasks for the orchestration runtime (Phase 2.0). Each task runs its own…, Publish due outbox events, then drive the simulated edge lifecycle., Snapshot of outbox health for alerting / dashboards., Flag stations whose edge agents missed their heartbeat window. (+4 more)

### Community 146 - "publish_pending"
Cohesion: 0.27
Nodes (13): publish_pending(), AsyncSession, Dispatch up to `limit` due events. Returns count successfully published.…, _emit_event(), A hook returning False leaves the event PENDING for a later retry., The worker's core drain loop must be idempotent and safe., test_emit_writes_pending_outbox_row(), test_hook_failure_marks_failed() (+5 more)

### Community 147 - "test_delivery.py"
Cohesion: 0.42
Nodes (8): _add_destinations(), _make_completed_job(), Phase 2.3 tests — data delivery pipeline triggered on job completion., Full loop: runtime drives QUEUED..COMPLETED and triggers delivery., test_list_delivery_jobs_scoped_to_org(), test_on_job_completed_creates_delivered_jobs(), test_on_job_completed_idempotent(), test_runtime_completes_job_and_delivers()

### Community 148 - "outbox_worker.py"
Cohesion: 0.39
Nodes (7): drain_once(), main(), Orchestration runtime dispatcher — polls the outbox, publishes due events, and…, _request_stop(), run(), drain(), Poll outbox events, publish them, fan out to per-org webhooks, and (in real-…

### Community 149 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

## Knowledge Gaps
- **495 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `ContractData`, `LineItem`, `QuoteResult` (+490 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TenantContext` connect `TenantContext` to `EdgeAgentService`, `StationService`, `FastAPI`, `MissionService`, `OperationsEngine`, `ContactPlanningService`, `simulate_edge.py`, `business.py`, `readiness.py`, `RegulatoryAuthorizationService`, `test_api.py`, `SGP4Engine`, `orchestration_runtime.py`, `keys.py`, `Base`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `EdgeNodeFactory` connect `EdgeNodeFactory` to `RFController`, `hal/__init__.py`, `ReceiverController`, `RecordingController`, `mock_controllers.py`, `interfaces.py`, `api/main.py`, `PowerController`, `MockModemController`, `AntennaController`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `Base` connect `Base` to `EdgeAgentService`, `FastAPI`, `OutboxEvent`, `OperationsEngine`, `ContactPlanningService`, `simulate_edge.py`, `readiness.py`, `business.py`, `asyncio`, `test_agent.py`, `RecurringMissionSweeper`, `RegulatoryAuthorizationService`, `test_webhooks.py`, `test_sla.py`, `api/main.py`, `events.py`, `keys.py`, `DeliveryService`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `TenantContext` (e.g. with `Organization` and `Role`) actually correct?**
  _`TenantContext` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `ObservationOrchestrator` (e.g. with `create_job()` and `list_job_events()`) actually correct?**
  _`ObservationOrchestrator` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `ContactPlanningService` (e.g. with `confirm_reservation()` and `create_contact_opportunities()`) actually correct?**
  _`ContactPlanningService` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `ContractData` to the rest of the system?**
  _495 weakly-connected nodes found - possible documentation gaps or missing edges._