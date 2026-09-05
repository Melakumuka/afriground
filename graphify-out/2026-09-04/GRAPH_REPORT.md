# Graph Report - afriGround  (2026-09-04)

## Corpus Check
- 219 files · ~178,951 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1966 nodes · 4950 edges · 124 communities (102 shown, 22 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 450 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2f9189af`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- edge.py
- ObservationJob
- routes/data.py
- EarthScene.tsx
- StationService
- api_keys.py
- MissionService
- OperationsEngine
- contact_planning.py
- Base
- readiness.py
- RegulatoryAuthorizationService
- tasks.py
- TenantContext
- useT
- [locale]/page.tsx
- test_webhooks.py
- test_sla.py
- compilerOptions
- booking_service.py
- api.ts
- NetworkRoutingService
- _post
- StationGatewayAdapter
- Config
- celestrak.ts
- UUID
- FastAPI
- commercial_engine.py
- scripts
- ContactPlanningService
- AntennaController
- keys.py
- devDependencies
- orchestration_runtime.py
- dependencies
- What You Must Do When Invoked
- test_orchestration_runtime.py
- test_agent.py
- booking/page.tsx
- RFController
- routes/regulatory.py
- What You Must Do When Invoked
- agent.py
- EdgeAgentService
- hal/__init__.py
- ReceiverController
- RecordingController
- mock_controllers.py
- interfaces.py
- gen_agent_certs.py
- services/__init__.py
- EdgeNodeFactory
- routes/tenancy.py
- matcher.py
- web/package.json
- layout.tsx
- PowerController
- station/page.tsx
- .find_optimal_station
- MockModemController
- healthz_check
- IsolatedObserver
- StateMachine
- next-intl
- data/page.tsx
- DeliveryService
- CinematicHero.tsx
- AGENTS.md
- CloudClient
- Settings
- graphify reference: extra exports and benchmark
- graphify reference: query, path, explain
- next.config.ts
- graphify.js
- entrypoint.sh
- run.sh
- eslint.config.mjs
- postprocessing
- three
- @types/node
- postcss.config.mjs
- i18n.ts
- proxy.ts
- bootstrap_state.sh
- userdata.sh
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- .agents/skills/graphify/references/extraction-spec.md
- MockZodiacMCSAdapter
- Walkthrough: Station Gateway Edge UI
- web/README.md
- emit
- contract_usage
- AfriGround Station Gateway
- web/AGENTS.md
- .get_job
- asyncio
- CachedJob
- opencode.json
- RecurringMissionSweeper
- commercial/page.tsx
- operator.py
- routing.py
- orchestration_metrics
- verify_token
- tenant_context_middleware

## God Nodes (most connected - your core abstractions)
1. `TenantContext` - 131 edges
2. `Base` - 80 edges
3. `ObservationJob` - 71 edges
4. `ObservationOrchestrator` - 70 edges
5. `_post()` - 63 edges
6. `ContactPlanningService` - 52 edges
7. `EdgeAgentService` - 46 edges
8. `RegulatoryAuthorizationService` - 45 edges
9. `useT()` - 41 edges
10. `GroundStation` - 40 edges

## Surprising Connections (you probably didn't know these)
- `test_agent_revoked_identity_rejected()` --uses--> `StationAgentIdentity`  [INFERRED]
  apps/api/tests/test_agent.py → apps/api/models/station_twin.py
- `get_job_details()` --uses--> `ExecutionReceipt`  [INFERRED]
  apps/api/routes/contact.py → apps/api/models/contact.py
- `submit_receipt()` --uses--> `ExecutionReceipt`  [INFERRED]
  apps/api/routes/edge.py → apps/api/models/contact.py
- `AgentDispatchService` --uses--> `ExecutionReceipt`  [INFERRED]
  apps/api/services/agent_dispatch.py → apps/api/models/contact.py
- `DataEngine` --uses--> `ExecutionReceipt`  [INFERRED]
  apps/api/services/data_engine.py → apps/api/models/contact.py

## Import Cycles
- None detected.

## Communities (124 total, 22 thin omitted)

### Community 0 - "edge.py"
Cohesion: 0.09
Nodes (43): decrypt_dict(), Decrypts a Fernet token string back into a dictionary., acknowledge_job(), ArtifactUploadRequest, get_assigned_jobs(), get_profile_detail(), get_station_profiles(), ingest_telemetry() (+35 more)

### Community 1 - "ObservationJob"
Cohesion: 0.11
Nodes (20): ObservationJob, Executable unit of work for the orchestrator / edge agent., Everything the agent needs to execute: contact window, RF config, mission…, Jobs scheduled on this agent's station in the given states (default: DISPATCHED…, JobNotFound, _now(), ObservationOrchestrator, AsyncSession (+12 more)

### Community 2 - "routes/data.py"
Cohesion: 0.10
Nodes (28): encrypt_dict(), Encrypts a dictionary into a Fernet token string., Dataset, add_destination(), download_dataset(), list_datasets(), list_destinations(), AsyncSession (+20 more)

### Community 3 - "EarthScene.tsx"
Cohesion: 0.07
Nodes (32): CinematicBackground(), EarthScene, SceneBoundary, Atmosphere(), Earth(), AFRICA_POLY, createEarthTexture(), drawRing() (+24 more)

### Community 4 - "StationService"
Cohesion: 0.12
Nodes (33): Tracked physical hardware at a station (antenna, SDR, rotator, clock, ...)., StationHardware, add_capability(), add_hardware(), add_license(), add_quality_score(), get_certification(), get_station() (+25 more)

### Community 5 - "api_keys.py"
Cohesion: 0.14
Nodes (25): APIKey, generate_api_key(), get_api_key_context(), _hash_key(), list_api_keys(), AsyncSession, UUID, API Key Authentication (Phase 3.1) — programmatic access for platform/GS… (+17 more)

### Community 6 - "MissionService"
Cohesion: 0.09
Nodes (40): MissionSLA, MissionTelecommandDefinition, MissionTelemetryDefinition, SLA requirements attached to a mission., Decoded TM parameter definition (frame-format-agnostic; XTCE-ready)., Structured telecommand definition for a mission profile., activate_mission(), create_constraint() (+32 more)

### Community 7 - "OperationsEngine"
Cohesion: 0.10
Nodes (34): MaintenanceEvent, create_incident(), create_maintenance(), evaluate_station_risk(), list_incidents(), list_maintenance(), AsyncSession, get (+26 more)

### Community 8 - "contact_planning.py"
Cohesion: 0.12
Nodes (19): ContactOpportunity, ExecutionReceipt, A feasible RF contact opportunity for a mission profile on a specific pass., Customer reservation against a contact opportunity., A confirmed, executable contact on the station schedule., Raw geometric pass: a spacecraft is geometrically visible from a station., Post-execution result report for an observation job. Generated by the Edge…, Reservation (+11 more)

### Community 9 - "Base"
Cohesion: 0.12
Nodes (34): Base, Contract, Organization, Role, User, Recorded SLA breach (Phase 3.0) — created by the runtime on job completion., SLASLAViolation, Operation (+26 more)

### Community 10 - "readiness.py"
Cohesion: 0.16
Nodes (17): Engineer's manual readiness confirmation for a job. Mandatory gate before…, StationReadinessEvent, Saved, certified station configuration for a specific satellite mission.…, StationOperationProfile, _now(), AsyncSession, datetime, HTTPException (+9 more)

### Community 11 - "RegulatoryAuthorizationService"
Cohesion: 0.13
Nodes (28): Regulatory license held by the station operator., Current certification state of a station (Digital Twin lifecycle)., Auditable certification state transitions., Structured RF capability of a station (replaces loose JSONB)., StationCapability, StationCertification, StationCertificationEvent, StationLicense (+20 more)

### Community 12 - "tasks.py"
Cohesion: 0.26
Nodes (12): Celery application for the AfriGround orchestration runtime (Phase 2.0). The…, check_heartbeats(), drain_outbox(), outbox_metrics(), Celery tasks for the orchestration runtime (Phase 2.0). Each task runs its own…, Publish due outbox events, then drive the simulated edge lifecycle., Snapshot of outbox health for alerting / dashboards., Flag stations whose edge agents missed their heartbeat window. (+4 more)

### Community 13 - "TenantContext"
Cohesion: 0.07
Nodes (26): AsyncSession, AsyncSession, TenantContext, authed_client(), client(), fixture, Route-level integration tests: real FastAPI app, real test DB, mocked Supabase…, A tenant without job.operate must get 403 on job endpoints. (+18 more)

### Community 14 - "useT"
Cohesion: 0.07
Nodes (30): ContractDashboard(), ContractData, MOCK_CONTRACT, CommercialQuotesPage(), LineItem, PRICING_TIERS, QuoteResult, ContactPage() (+22 more)

### Community 15 - "[locale]/page.tsx"
Cohesion: 0.12
Nodes (22): CountUp(), COAST, CoverageSection(), CoverageText, proj(), DataFlowText, DataFlowVisualization(), EarthIntelligence() (+14 more)

### Community 16 - "test_webhooks.py"
Cohesion: 0.06
Nodes (60): Idempotent per-webhook delivery record for a published outbox event (Phase 3.1)…, SupportTicket, Webhook, WebhookDelivery, create_ticket(), list_tickets(), AsyncSession, get (+52 more)

### Community 17 - "test_sla.py"
Cohesion: 0.14
Nodes (18): _now(), AsyncSession, datetime, UUID, SLA Enforcement (Phase 3.0) — evaluates mission SLAs when an observation job…, Evaluate all SLAs for the job's mission against its outcome. Creates an…, SLAService, _add_sla() (+10 more)

### Community 18 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 19 - "booking_service.py"
Cohesion: 0.20
Nodes (14): Booking, PassPrediction, Schedule, BookingService, AsyncSession, UUID, Transition a Pass Prediction into a REQUESTED Booking. Also runs compatibility…, Transition a Booking to CONFIRMED and its Schedule to SCHEDULED. (+6 more)

### Community 20 - "api.ts"
Cohesion: 0.12
Nodes (39): CONTACT_JOB_RE, DATASET_DOWNLOAD_RE, dynamic, GET(), MISSION_CHILD_RE, POST(), resolvePath(), STATION_CHILD_RE (+31 more)

### Community 21 - "NetworkRoutingService"
Cohesion: 0.14
Nodes (15): network_ranking(), AsyncSession, get, AsyncSession, NetworkRoutingService, AsyncSession, UUID, Composite routing score (0-100) for one station, with contributing factors. (+7 more)

### Community 22 - "_post"
Cohesion: 0.29
Nodes (20): confirm_reservation(), create_contact_opportunities(), create_job(), create_reservation(), generate_visibility_opportunities(), get_job_details(), _job_dict(), list_job_events() (+12 more)

### Community 23 - "StationGatewayAdapter"
Cohesion: 0.08
Nodes (12): ABC, Command the antenna to immediately stow to safe position. NOTE: per the…, Immediately kill all RF transmissions. NOTE: per the Isolated Observer Profile,…, Abstract base class for interfacing with physical station hardware (MCS, ACU,…, Returns the extended Safran health snapshot used by the dashboard:…, Subscribe to RM Port 4000. Real adapter: open a TCP socket to…, FTP pull of the MCS activity table. Returns the file content (XML)., FTP pull of completed pass XML reports from D:\\MCS_PUBLIC\\Pass. (+4 more)

### Community 24 - "Config"
Cohesion: 0.18
Nodes (10): Config, BaseSettings, Settings, CRTRedundancyLog, get_db(), init_db(), LCBEngagementLog, Local Control Box (hand-paddle) engagement log. (+2 more)

### Community 25 - "celestrak.ts"
Cohesion: 0.15
Nodes (19): computePasses(), eciToEcf(), geodeticToEcf(), GET(), PassInfo, GET(), epochToUtc(), FALLBACK_TLES (+11 more)

### Community 26 - "UUID"
Cohesion: 0.23
Nodes (8): _now(), datetime, UUID, Return a reason string when a mission operational constraint makes this…, Generate opportunities and (best) reservation for a mission profile., ContactOpportunity, Reservation, VisibilityOpportunity

### Community 27 - "FastAPI"
Cohesion: 0.16
Nodes (20): get_current_user(), get_current_user_db(), get_db_session(), AsyncSession, Extract user information from the verified token payload. In a real app, this…, Resolve the JWT subject to the persisted User row (Phase 1 tenancy)., API Routes — Business tier (Phase 3.0): SLA violations, contract usage,…, Manually run the recurring-mission booking sweep for the org (the Celery beat… (+12 more)

### Community 28 - "commercial_engine.py"
Cohesion: 0.17
Nodes (22): Quote, accept_quote(), create_contract(), create_quote(), create_recurring_mission(), get_contract_usage(), AsyncSession, get (+14 more)

### Community 29 - "scripts"
Cohesion: 0.10
Nodes (20): description, engines, node, pnpm, name, packageManager, private, scripts (+12 more)

### Community 30 - "ContactPlanningService"
Cohesion: 0.11
Nodes (40): DataDeliveryDestination, Mission, MissionOperationalConstraint, MissionProfile, MissionRFProfile, Operational campaign against a spacecraft., Versioned operational profile of a mission., RF plan for a mission profile: TX/RX constraints per band. (+32 more)

### Community 31 - "AntennaController"
Cohesion: 0.12
Nodes (9): AntennaController, AntennaPosition, BaseModel, Controls antenna pointing and tracking., Get the current antenna azimuth/elevation., Command the antenna to slew to a specific position., Begin auto-tracking a satellite using its TLE., Emergency stop / park the antenna. (+1 more)

### Community 32 - "keys.py"
Cohesion: 0.23
Nodes (15): create_key(), key_me(), KeyCreateRequest, KeyCreateResponse, KeyListResponse, KeyMeResponse, list_keys(), AsyncSession (+7 more)

### Community 33 - "devDependencies"
Cohesion: 0.11
Nodes (19): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/nodemailer, @types/react, @types/react-dom (+11 more)

### Community 34 - "orchestration_runtime.py"
Cohesion: 0.12
Nodes (24): JobEvent, State transition history for observation jobs (idempotent audit)., main(), Orchestration runtime dispatcher — polls the outbox, publishes due events, and…, _request_stop(), run(), dispatch_due_jobs(), drain() (+16 more)

### Community 36 - "dependencies"
Cohesion: 0.12
Nodes (17): dependencies, next, nodemailer, react, react-dom, @react-three/drei, @react-three/fiber, @react-three/postprocessing (+9 more)

### Community 37 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 38 - "test_orchestration_runtime.py"
Cohesion: 0.23
Nodes (15): metrics(), Outbox health/backpressure summary for the ops endpoint., backoff_seconds(), Exponential backoff capped at RETRY_MAX_S: base * 2**(attempt-1)., _emit(), Phase 2.0 orchestration runtime tests: outbox retry/backoff, simulated job…, A hook that stops failing lets the retried event publish., _register_hook() (+7 more)

### Community 39 - "test_agent.py"
Cohesion: 0.10
Nodes (27): GroundStation, get_agent_identity(), AsyncSession, Edge Agent mTLS Identity (Phase 4.0) — resolves a client certificate to a…, Resolve the mTLS client certificate CN to an active agent identity., AgentDispatchService, _now(), AsyncSession (+19 more)

### Community 40 - "booking/page.tsx"
Cohesion: 0.16
Nodes (10): BookingWizard(), PassesResponse, Quote, SupportPortal(), StationNetworkMap(), GroundStationNode, STATIONS, Mission (+2 more)

### Community 41 - "RFController"
Cohesion: 0.18
Nodes (4): Controls RF chain configuration., RFController, RFStatus, MockRFController

### Community 42 - "routes/regulatory.py"
Cohesion: 0.44
Nodes (8): agent_heartbeat(), evaluate_tx(), AsyncSession, UUID, API Routes — Regulatory Enforcement (Phase 1.5), register_station(), report_time_status(), transition_certification()

### Community 43 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 44 - "agent.py"
Cohesion: 0.22
Nodes (20): acknowledge_job(), agent_heartbeat(), agent_telemetry(), agent_time_status(), assigned_jobs(), HeartbeatRequest, job_detail(), AsyncSession (+12 more)

### Community 45 - "EdgeAgentService"
Cohesion: 0.13
Nodes (29): Incident, Edge agent identity for a station (mTLS bridge, Phase 4.0)., Per-agent heartbeat records used by the missed-heartbeat watchdog., Structured telemetry readings reported by station agents., Periodic quality scoring for a station (feeds routing/risk)., Time synchronization quality reported by the station agent., StationAgentIdentity, StationHeartbeat (+21 more)

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

### Community 52 - "services/__init__.py"
Cohesion: 0.17
Nodes (8): AsyncSession, PassResult, BaseModel, datetime, Predict satellite passes over a specific ground station within a time window., SGP4Engine, EarthSatellite, Topos

### Community 53 - "EdgeNodeFactory"
Cohesion: 0.24
Nodes (6): EdgeNodeFactory, Factory for creating hardware controller instances. In development, returns…, Controls Software Defined Radio equipment., Returns spectrum analysis data., SDRController, MockSDRController

### Community 54 - "routes/tenancy.py"
Cohesion: 0.36
Nodes (10): grant_permission(), list_audit_logs(), list_permissions(), list_roles(), my_tenant(), AsyncSession, get, UUID (+2 more)

### Community 55 - "matcher.py"
Cohesion: 0.36
Nodes (7): CompatibilityResult, GroundStationCapabilities, MatcherResult, BaseModel, Enum, str, SatelliteRFRequest

### Community 56 - "web/package.json"
Cohesion: 0.20
Nodes (9): name, packageManager, private, scripts, build, dev, lint, start (+1 more)

### Community 57 - "layout.tsx"
Cohesion: 0.24
Nodes (4): ibmPlexMono, spaceGrotesk, Footer(), Navbar()

### Community 58 - "PowerController"
Cohesion: 0.31
Nodes (4): PowerController, PowerStatus, Monitors and controls power systems., MockPowerController

### Community 59 - "station/page.tsx"
Cohesion: 0.22
Nodes (6): StationHealthDashboard(), StationRisk, TelemetryData, Agent, Station, TimeStatus

### Community 60 - ".find_optimal_station"
Cohesion: 0.40
Nodes (4): datetime, UUID, Evaluate all ground stations in the network and return the ID of the optimal…, Called when a scheduled pass is about to fail due to sudden hardware…

### Community 62 - "healthz_check"
Cohesion: 0.33
Nodes (6): health_check(), healthz_check(), AsyncSession, get, Liveness probe (Phase 3.3): verifies DB reachability. 503 when down., read_users_me()

### Community 63 - "IsolatedObserver"
Cohesion: 0.11
Nodes (8): IsolatedObserver, Read-only Safran Pro 730 SX health/status aggregator. Never issues a command to…, RM 4000 ping + last packet age., Inferred from ACU RM stream., Inferred from ACU RM stream., Safran PC Saphir D: occupancy percent, Nominal vs Spare vs SPOF, Interpass + rise-angle conflicts

### Community 66 - "data/page.tsx"
Cohesion: 0.40
Nodes (5): DataCatalog(), DatasetRow, mapDataset(), MOCK_DATASETS, Dataset

### Community 67 - "DeliveryService"
Cohesion: 0.17
Nodes (18): DataDeliveryJob, _checksum(), DeliveryService, _now(), AsyncSession, datetime, UUID, Data Delivery Pipeline (Phase 2.3) — when an observation job completes, the… (+10 more)

### Community 68 - "CinematicHero.tsx"
Cohesion: 0.47
Nodes (4): AfriGroundTechnicalHUD(), HudText, CinematicHero(), HeroText

### Community 69 - "AGENTS.md"
Cohesion: 0.13
Nodes (14): CURRENT REPOSITORY STATE, FINAL INSTRUCTIONS, graphify, ROLE AND CONTEXT, STEP 1: Upgrade Cloud Database Models, STEP 2: Create the Station Gateway App Skeleton, STEP 3: Implement the Station Gateway Adapter Pattern, STEP 4: Build the Local Operator Console (Edge UI) (+6 more)

### Community 79 - "CloudClient"
Cohesion: 0.15
Nodes (3): CloudClient, Enforces Safran Pro 730 SX readiness checks before allowing cloud execution., ReadinessService

### Community 81 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 83 - "graphify reference: query, path, explain"
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

### Community 120 - "MockZodiacMCSAdapter"
Cohesion: 0.09
Nodes (7): MockZodiacMCSAdapter, Mock activity table XML., Mock list of completed-pass report XML files., Mock implementation of the Safran Pro 730 SX / Zodiac PFM730 MCS adapter.…, Test helper: set CRT state to 'nominal' | 'spare' | 'spof'., Extended Safran health snapshot for the dashboard., Mock RM Port 4000 stream — yields one Az/El sample.

### Community 128 - "Walkthrough: Station Gateway Edge UI"
Cohesion: 0.29
Nodes (6): 🖥️ 1. Edge Operator Console (`apps/station-gateway/templates/`), 🛑 2. The Readiness Gate (Safety Interlock), 🚨 3. Local-First Emergency Abort, 📄 4. Post-Pass Execution Receipts, 📚 5. User Guide Expanded, Walkthrough: Station Gateway Edge UI

### Community 133 - "web/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 134 - "emit"
Cohesion: 0.13
Nodes (30): OutboxEvent, Transactional outbox: durable events emitted with their owning transaction., drain_once(), dispatch_job_to_webhook(), dispatch_receipt_to_webhook(), dispatch_station_to_webhook(), _json_dumps(), _post_webhook() (+22 more)

### Community 135 - "contract_usage"
Cohesion: 0.23
Nodes (12): contract_usage(), ContractUsageResponse, list_contracts(), AsyncSession, BaseModel, get, UUID, List contracts for the tenant. (+4 more)

### Community 145 - ".get_job"
Cohesion: 0.33
Nodes (4): ExecutionReceipt, UUID, Persist an execution receipt; terminal state is applied if the job has not…, Agent-driven execution-chain transition (validated against AGENT_CHAIN).

### Community 146 - "asyncio"
Cohesion: 0.13
Nodes (20): do_run_migrations(), include_name(), include_object(), In this scenario we need to create an Engine and associate a connection with…, Run migrations in 'online' mode., Only manage application tables in the 'public' schema; never touch…, Filter removed tables from non-public schemas (include_object is not called for…, Run migrations in 'offline' mode. This configures the context with just a URL… (+12 more)

### Community 148 - "CachedJob"
Cohesion: 0.23
Nodes (5): CachedJob, CachedProfile, ExecutionService, Validates the 12 Safran safety checks + LCB + CRT SPOF. Returns (is_ready,…, BackgroundWorker

### Community 149 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 152 - "RecurringMissionSweeper"
Cohesion: 0.13
Nodes (11): RecurringMission, datetime, UUID, Customer accepts a quote — transitions bookings to RESERVED., Get contract details including usage against reserved capacity. Usage is…, Sum completed contact durations (minutes) for the org in the contract window., Create a recurring mission that auto-generates bookings for X passes/day., Auto-generates bookings for active recurring missions from TLE pass… (+3 more)

### Community 154 - "commercial/page.tsx"
Cohesion: 0.29
Nodes (5): CommercialDashboard(), Contract, MOCK_CONTRACTS, MOCK_VIOLATIONS, SlaViolation

### Community 155 - "operator.py"
Cohesion: 0.15
Nodes (20): get_adapter(), FirewallAuditLog, LocalActionAck, Per-rule firewall posture audit. Local-first; never assumes cloud., Engineer acknowledgement of the passive / no-active-commands notice., confirm_ready(), dashboard(), get_job_status() (+12 more)

### Community 156 - "routing.py"
Cohesion: 0.15
Nodes (11): FailoverResponse, AsyncSession, BaseModel, UUID, API Routes — Multi-station Routing & Failover, Manually trigger an automatic failover for a scheduled pass. The routing engine…, trigger_auto_failover(), Real-time Telemetry WebSocket — Streams live pass execution data to the… (+3 more)

### Community 167 - "orchestration_metrics"
Cohesion: 0.67
Nodes (3): orchestration_metrics(), AsyncSession, get

### Community 169 - "verify_token"
Cohesion: 0.67
Nodes (3): Verify the JWT token from Supabase., verify_token(), HTTPAuthorizationCredentials

### Community 170 - "tenant_context_middleware"
Cohesion: 0.67
Nodes (3): Stamp request state with the verified JWT subject (tenant resolution happens in…, tenant_context_middleware(), middleware

## Knowledge Gaps
- **233 isolated node(s):** `withNextIntl`, `nextConfig`, `locales`, `PassesResponse`, `Quote` (+228 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TenantContext` connect `TenantContext` to `edge.py`, `ObservationJob`, `StationService`, `MissionService`, `contract_usage`, `contact_planning.py`, `Base`, `readiness.py`, `RegulatoryAuthorizationService`, `test_webhooks.py`, `NetworkRoutingService`, `_post`, `FastAPI`, `ContactPlanningService`, `keys.py`, `orchestration_metrics`, `routes/regulatory.py`, `EdgeAgentService`, `routes/tenancy.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `Base` connect `Base` to `ObservationJob`, `routes/data.py`, `StationService`, `api_keys.py`, `emit`, `MissionService`, `contact_planning.py`, `OperationsEngine`, `readiness.py`, `RegulatoryAuthorizationService`, `test_webhooks.py`, `asyncio`, `booking_service.py`, `CachedJob`, `RecurringMissionSweeper`, `Config`, `operator.py`, `commercial_engine.py`, `ContactPlanningService`, `orchestration_runtime.py`, `test_agent.py`, `EdgeAgentService`, `DeliveryService`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `_post()` connect `_post` to `edge.py`, `keys.py`, `routes/data.py`, `StationService`, `MissionService`, `OperationsEngine`, `routes/regulatory.py`, `agent.py`, `operator.py`, `test_webhooks.py`, `routing.py`, `routes/tenancy.py`, `FastAPI`, `commercial_engine.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `TenantContext` (e.g. with `Organization` and `Role`) actually correct?**
  _`TenantContext` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `ObservationJob` (e.g. with `get_job_details()` and `_job_dict()`) actually correct?**
  _`ObservationJob` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ObservationOrchestrator` (e.g. with `create_job()` and `list_job_events()`) actually correct?**
  _`ObservationOrchestrator` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `withNextIntl`, `nextConfig`, `locales` to the rest of the system?**
  _233 weakly-connected nodes found - possible documentation gaps or missing edges._