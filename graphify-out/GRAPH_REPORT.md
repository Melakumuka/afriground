# Graph Report - afriGround  (2026-09-05)

## Corpus Check
- 220 files · ~179,100 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1977 nodes · 4979 edges · 121 communities (94 shown, 27 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 454 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5796fe9d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- EdgeAgentService
- ObservationJob
- routes/data.py
- EarthScene.tsx
- StationService
- api_keys.py
- MissionService
- OperationsEngine
- ContactPlanningService
- services/tenancy.py
- support.py
- RegulatoryAuthorizationService
- tasks.py
- test_api.py
- useT
- CoverageSection.tsx
- test_webhooks.py
- test_sla.py
- compilerOptions
- booking_service.py
- [locale]/page.tsx
- keys.py
- TenantContext
- StationGatewayAdapter
- operator.py
- celestrak.ts
- audit_page
- CachedJob
- CommercialEngine
- package.json
- agent_sim.py
- AntennaController
- .find_optimal_station
- devDependencies
- StateMachine
- dependencies
- What You Must Do When Invoked
- test_token.ts
- test_agent.py
- booking/page.tsx
- RFController
- .__init__
- What You Must Do When Invoked
- agent.py
- .__init__
- hal/__init__.py
- ReceiverController
- RecordingController
- mock_controllers.py
- interfaces.py
- gen_agent_certs.py
- SGP4Engine
- EdgeNodeFactory
- web/package.json
- layout.tsx
- PowerController
- api.ts
- Base
- MockModemController
- tenant_context_middleware
- IsolatedObserver
- asyncio
- data/page.tsx
- DeliveryService
- CinematicHero.tsx
- AGENTS.md
- CloudClient
- Settings
- graphify reference: extra exports and benchmark
- Settings
- graphify reference: query, path, explain
- react-dom
- next.config.ts
- graphify.js
- entrypoint.sh
- run.sh
- eslint.config.mjs
- @tailwindcss/postcss
- postprocessing
- three
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
- business.py
- AfriGround Station Gateway
- web/AGENTS.md
- env.py
- BackgroundWorker
- opencode.json
- BaseModel
- commercial/page.tsx
- pass_console
- routing.py
- simulate_edge.py
- FastAPI

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
- `get_current_user_db()` --uses--> `User`  [INFERRED]
  apps/api/auth.py → apps/api/models/core.py
- `EdgeNodeFactory` --uses--> `AntennaController`  [INFERRED]
  apps/api/hal/__init__.py → apps/api/hal/interfaces.py
- `EdgeNodeFactory` --uses--> `ModemController`  [INFERRED]
  apps/api/hal/__init__.py → apps/api/hal/interfaces.py
- `EdgeNodeFactory` --uses--> `PowerController`  [INFERRED]
  apps/api/hal/__init__.py → apps/api/hal/interfaces.py
- `EdgeNodeFactory` --uses--> `ReceiverController`  [INFERRED]
  apps/api/hal/__init__.py → apps/api/hal/interfaces.py

## Import Cycles
- None detected.

## Communities (121 total, 27 thin omitted)

### Community 0 - "EdgeAgentService"
Cohesion: 0.06
Nodes (66): decrypt_dict(), Decrypts a Fernet token string back into a dictionary., Incident, Per-agent heartbeat records used by the missed-heartbeat watchdog., Structured telemetry readings reported by station agents., StationHeartbeat, StationTelemetryReading, acknowledge_job() (+58 more)

### Community 1 - "ObservationJob"
Cohesion: 0.05
Nodes (50): ObservationJob, Engineer's manual readiness confirmation for a job. Mandatory gate before…, Executable unit of work for the orchestrator / edge agent., StationReadinessEvent, JobEvent, State transition history for observation jobs (idempotent audit)., Saved, certified station configuration for a specific satellite mission.…, StationOperationProfile (+42 more)

### Community 2 - "routes/data.py"
Cohesion: 0.10
Nodes (27): encrypt_dict(), Encrypts a dictionary into a Fernet token string., add_destination(), download_dataset(), list_datasets(), list_destinations(), AsyncSession, get (+19 more)

### Community 3 - "EarthScene.tsx"
Cohesion: 0.07
Nodes (32): CinematicBackground(), EarthScene, SceneBoundary, Atmosphere(), Earth(), AFRICA_POLY, createEarthTexture(), drawRing() (+24 more)

### Community 4 - "StationService"
Cohesion: 0.13
Nodes (31): add_capability(), add_hardware(), add_license(), add_quality_score(), get_certification(), get_station(), list_agents(), list_capabilities() (+23 more)

### Community 5 - "api_keys.py"
Cohesion: 0.14
Nodes (25): APIKey, generate_api_key(), get_api_key_context(), _hash_key(), list_api_keys(), AsyncSession, UUID, API Key Authentication (Phase 3.1) — programmatic access for platform/GS… (+17 more)

### Community 6 - "MissionService"
Cohesion: 0.12
Nodes (33): activate_mission(), create_constraint(), create_mission(), create_profile(), create_rf_profile(), create_sla(), create_spacecraft(), create_tc_command() (+25 more)

### Community 7 - "OperationsEngine"
Cohesion: 0.06
Nodes (46): MaintenanceEvent, network_ranking(), AsyncSession, get, create_incident(), create_maintenance(), evaluate_station_risk(), list_incidents() (+38 more)

### Community 8 - "ContactPlanningService"
Cohesion: 0.13
Nodes (24): ContactOpportunity, A feasible RF contact opportunity for a mission profile on a specific pass., Customer reservation against a contact opportunity., A confirmed, executable contact on the station schedule., Raw geometric pass: a spacecraft is geometrically visible from a station., Reservation, ScheduledContact, VisibilityOpportunity (+16 more)

### Community 9 - "services/tenancy.py"
Cohesion: 0.12
Nodes (36): Organization, Role, User, AuditLog, Permission, RolePermission, grant_permission(), list_audit_logs() (+28 more)

### Community 10 - "support.py"
Cohesion: 0.15
Nodes (20): SupportTicket, create_ticket(), list_tickets(), AsyncSession, get, UUID, API Routes — Support Ticketing Engine, AsyncSession (+12 more)

### Community 11 - "RegulatoryAuthorizationService"
Cohesion: 0.12
Nodes (29): Regulatory license held by the station operator., Current certification state of a station (Digital Twin lifecycle)., Auditable certification state transitions., Structured RF capability of a station (replaces loose JSONB)., Time synchronization quality reported by the station agent., StationCapability, StationCertification, StationCertificationEvent (+21 more)

### Community 12 - "tasks.py"
Cohesion: 0.26
Nodes (12): Celery application for the AfriGround orchestration runtime (Phase 2.0). The…, check_heartbeats(), drain_outbox(), outbox_metrics(), Celery tasks for the orchestration runtime (Phase 2.0). Each task runs its own…, Publish due outbox events, then drive the simulated edge lifecycle., Snapshot of outbox health for alerting / dashboards., Flag stations whose edge agents missed their heartbeat window. (+4 more)

### Community 13 - "test_api.py"
Cohesion: 0.07
Nodes (23): authed_client(), client(), fixture, Route-level integration tests: real FastAPI app, real test DB, mocked Supabase…, A tenant without job.operate must get 403 on job endpoints., POST /api/v1/stations/{id}/tx requires station.manage; a tenant without…, TestClient with its own engine; connections are created inside the portal loop…, GET /api/v1/orchestration/metrics requires platform.admin. (+15 more)

### Community 14 - "useT"
Cohesion: 0.07
Nodes (30): ContractDashboard(), ContractData, MOCK_CONTRACT, CommercialQuotesPage(), LineItem, PRICING_TIERS, QuoteResult, ContactPage() (+22 more)

### Community 15 - "CoverageSection.tsx"
Cohesion: 0.10
Nodes (20): CountUp(), COAST, CoverageSection(), CoverageText, proj(), DataFlowText, DataFlowVisualization(), EarthIntelligence() (+12 more)

### Community 16 - "test_webhooks.py"
Cohesion: 0.09
Nodes (40): Idempotent per-webhook delivery record for a published outbox event (Phase 3.1)…, Webhook, WebhookDelivery, create_webhook(), delete_webhook(), list_webhooks(), AsyncSession, BaseModel (+32 more)

### Community 17 - "test_sla.py"
Cohesion: 0.19
Nodes (18): MissionSLA, SLA requirements attached to a mission., Recorded SLA breach (Phase 3.0) — created by the runtime on job completion., SLASLAViolation, _now(), datetime, SLA Enforcement (Phase 3.0) — evaluates mission SLAs when an observation job…, _add_sla() (+10 more)

### Community 18 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 19 - "booking_service.py"
Cohesion: 0.17
Nodes (15): BookingService, AsyncSession, UUID, Transition a Pass Prediction into a REQUESTED Booking. Also runs compatibility…, Transition a Booking to CONFIRMED and its Schedule to SCHEDULED., CompatibilityEngine, CompatibilityResult, GroundStationCapabilities (+7 more)

### Community 20 - "[locale]/page.tsx"
Cohesion: 0.14
Nodes (27): CONTACT_JOB_RE, DATASET_DOWNLOAD_RE, dynamic, GET(), MISSION_CHILD_RE, resolvePath(), STATION_CHILD_RE, LandingPage() (+19 more)

### Community 21 - "keys.py"
Cohesion: 0.23
Nodes (15): create_key(), key_me(), KeyCreateRequest, KeyCreateResponse, KeyListResponse, KeyMeResponse, list_keys(), AsyncSession (+7 more)

### Community 22 - "TenantContext"
Cohesion: 0.15
Nodes (33): Manually run the recurring-mission booking sweep for the org (the Celery beat…, trigger_recurring_booking(), confirm_reservation(), create_contact_opportunities(), create_job(), create_reservation(), generate_visibility_opportunities(), get_job_details() (+25 more)

### Community 23 - "StationGatewayAdapter"
Cohesion: 0.08
Nodes (12): ABC, Command the antenna to immediately stow to safe position. NOTE: per the…, Immediately kill all RF transmissions. NOTE: per the Isolated Observer Profile,…, Abstract base class for interfacing with physical station hardware (MCS, ACU,…, Returns the extended Safran health snapshot used by the dashboard:…, Subscribe to RM Port 4000. Real adapter: open a TCP socket to…, FTP pull of the MCS activity table. Returns the file content (XML)., FTP pull of completed pass XML reports from D:\\MCS_PUBLIC\\Pass. (+4 more)

### Community 24 - "operator.py"
Cohesion: 0.34
Nodes (6): get_adapter(), Config, init_db(), LocalActionAck, Engineer acknowledgement of the passive / no-active-commands notice., lifespan()

### Community 25 - "celestrak.ts"
Cohesion: 0.15
Nodes (19): computePasses(), eciToEcf(), geodeticToEcf(), GET(), PassInfo, GET(), epochToUtc(), FALLBACK_TLES (+11 more)

### Community 26 - "audit_page"
Cohesion: 0.22
Nodes (10): CRTRedundancyLog, get_db(), LCBEngagementLog, Local Control Box (hand-paddle) engagement log., CRT (S/N 19019) redundancy state log., audit_page(), AsyncSession, get (+2 more)

### Community 27 - "CachedJob"
Cohesion: 0.27
Nodes (6): CachedJob, CachedProfile, ExecutionService, Validates the 12 Safran safety checks + LCB + CRT SPOF. Returns (is_ready,…, Enforces Safran Pro 730 SX readiness checks before allowing cloud execution., ReadinessService

### Community 28 - "CommercialEngine"
Cohesion: 0.26
Nodes (12): accept_quote(), create_contract(), create_quote(), create_recurring_mission(), get_contract_usage(), AsyncSession, get, UUID (+4 more)

### Community 29 - "package.json"
Cohesion: 0.17
Nodes (11): description, name, private, scripts, build, dev, lint, start (+3 more)

### Community 30 - "agent_sim.py"
Cohesion: 0.11
Nodes (35): Mission, MissionRFProfile, MissionTelecommandDefinition, MissionTelemetryDefinition, Operational campaign against a spacecraft., RF plan for a mission profile: TX/RX constraints per band., Decoded TM parameter definition (frame-format-agnostic; XTCE-ready)., Operational twin of a satellite: separates spacecraft hardware from campaigns. (+27 more)

### Community 31 - "AntennaController"
Cohesion: 0.12
Nodes (9): AntennaController, AntennaPosition, BaseModel, Controls antenna pointing and tracking., Get the current antenna azimuth/elevation., Command the antenna to slew to a specific position., Begin auto-tracking a satellite using its TLE., Emergency stop / park the antenna. (+1 more)

### Community 32 - ".find_optimal_station"
Cohesion: 0.40
Nodes (4): datetime, UUID, Evaluate all ground stations in the network and return the ID of the optimal…, Called when a scheduled pass is about to fail due to sudden hardware…

### Community 33 - "devDependencies"
Cohesion: 0.11
Nodes (19): devDependencies, eslint, eslint-config-next, tailwindcss, @types/node, @types/nodemailer, @types/react, @types/react-dom (+11 more)

### Community 36 - "dependencies"
Cohesion: 0.12
Nodes (17): dependencies, next, next-intl, nodemailer, react, @react-three/drei, @react-three/fiber, @react-three/postprocessing (+9 more)

### Community 37 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (26): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+18 more)

### Community 38 - "test_token.ts"
Cohesion: 0.83
Nodes (3): b64url(), serviceToken(), test()

### Community 39 - "test_agent.py"
Cohesion: 0.12
Nodes (27): ExecutionReceipt, Post-execution result report for an observation job. Generated by the Edge…, Edge agent identity for a station (mTLS bridge, Phase 4.0)., StationAgentIdentity, AgentDispatchService, _now(), AsyncSession, BaseModel (+19 more)

### Community 40 - "booking/page.tsx"
Cohesion: 0.13
Nodes (13): BookingWizard(), PassesResponse, Quote, INITIAL_DEMO_TICKETS, SupportPortal(), SupportTicketItem, TicketLog, StationNetworkMap() (+5 more)

### Community 41 - "RFController"
Cohesion: 0.18
Nodes (4): Controls RF chain configuration., RFController, RFStatus, MockRFController

### Community 43 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 44 - "agent.py"
Cohesion: 0.18
Nodes (23): acknowledge_job(), agent_heartbeat(), agent_telemetry(), agent_time_status(), assigned_jobs(), HeartbeatRequest, job_detail(), AsyncSession (+15 more)

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
Cohesion: 0.17
Nodes (8): AsyncSession, PassResult, BaseModel, datetime, Predict satellite passes over a specific ground station within a time window., SGP4Engine, EarthSatellite, Topos

### Community 53 - "EdgeNodeFactory"
Cohesion: 0.24
Nodes (6): EdgeNodeFactory, Factory for creating hardware controller instances. In development, returns…, Controls Software Defined Radio equipment., Returns spectrum analysis data., SDRController, MockSDRController

### Community 56 - "web/package.json"
Cohesion: 0.18
Nodes (10): engines, node, name, private, scripts, build, dev, lint (+2 more)

### Community 57 - "layout.tsx"
Cohesion: 0.20
Nodes (6): ibmPlexMono, spaceGrotesk, Footer(), Navbar(), NavCategory, NavItem

### Community 58 - "PowerController"
Cohesion: 0.31
Nodes (4): PowerController, PowerStatus, Monitors and controls power systems., MockPowerController

### Community 59 - "api.ts"
Cohesion: 0.12
Nodes (23): POST(), StationHealthDashboard(), StationRisk, TelemetryData, Agent, api(), apiPost(), b64url() (+15 more)

### Community 60 - "Base"
Cohesion: 0.16
Nodes (25): Base, Contract, Quote, OutboxEvent, Transactional outbox: durable events emitted with their owning transaction., Booking, Operation, PassPrediction (+17 more)

### Community 62 - "tenant_context_middleware"
Cohesion: 0.67
Nodes (3): Stamp request state with the verified JWT subject (tenant resolution happens in…, tenant_context_middleware(), middleware

### Community 63 - "IsolatedObserver"
Cohesion: 0.11
Nodes (8): IsolatedObserver, Read-only Safran Pro 730 SX health/status aggregator. Never issues a command to…, RM 4000 ping + last packet age., Inferred from ACU RM stream., Inferred from ACU RM stream., Safran PC Saphir D: occupancy percent, Nominal vs Spare vs SPOF, Interpass + rise-angle conflicts

### Community 64 - "asyncio"
Cohesion: 0.46
Nodes (7): _alembic_config(), Guard against the tiger/topology regression: the migration must never emit DROP…, _run_upgrade_head(), test_migration_applies_cleanly(), test_migration_is_idempotent(), test_no_extension_schema_drops(), asyncio

### Community 66 - "data/page.tsx"
Cohesion: 0.33
Nodes (6): DataCatalog(), DatasetRow, EgressDestination, mapDataset(), MOCK_DATASETS, Dataset

### Community 67 - "DeliveryService"
Cohesion: 0.17
Nodes (20): DataDeliveryDestination, DataDeliveryJob, Dataset, _checksum(), DeliveryService, _now(), AsyncSession, datetime (+12 more)

### Community 68 - "CinematicHero.tsx"
Cohesion: 0.47
Nodes (4): AfriGroundTechnicalHUD(), HudText, CinematicHero(), HeroText

### Community 69 - "AGENTS.md"
Cohesion: 0.13
Nodes (14): CURRENT REPOSITORY STATE, FINAL INSTRUCTIONS, graphify, ROLE AND CONTEXT, STEP 1: Upgrade Cloud Database Models, STEP 2: Create the Station Gateway App Skeleton, STEP 3: Implement the Station Gateway Adapter Pattern, STEP 4: Build the Local Operator Console (Edge UI) (+6 more)

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
Cohesion: 0.06
Nodes (58): drain_once(), main(), Orchestration runtime dispatcher — polls the outbox, publishes due events, and…, _request_stop(), run(), _now(), datetime, UUID (+50 more)

### Community 135 - "business.py"
Cohesion: 0.24
Nodes (13): contract_usage(), ContractUsageResponse, list_contracts(), AsyncSession, BaseModel, get, UUID, API Routes — Business tier (Phase 3.0): SLA violations, contract usage,… (+5 more)

### Community 146 - "env.py"
Cohesion: 0.19
Nodes (13): do_run_migrations(), include_name(), include_object(), In this scenario we need to create an Engine and associate a connection with…, Run migrations in 'online' mode., Only manage application tables in the 'public' schema; never touch…, Filter removed tables from non-public schemas (include_object is not called for…, Run migrations in 'offline' mode. This configures the context with just a URL… (+5 more)

### Community 149 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 152 - "BaseModel"
Cohesion: 0.13
Nodes (14): ContractCreateRequest, ContractResponse, InvoiceItem, InvoiceResponse, BaseModel, UUID, QuoteCreateRequest, QuoteResponse (+6 more)

### Community 154 - "commercial/page.tsx"
Cohesion: 0.29
Nodes (5): CommercialDashboard(), Contract, MOCK_CONTRACTS, MOCK_VIOLATIONS, SlaViolation

### Community 155 - "pass_console"
Cohesion: 0.17
Nodes (17): FirewallAuditLog, Per-rule firewall posture audit. Local-first; never assumes cloud., confirm_ready(), dashboard(), get_job_status(), local_action_ack(), pass_console(), AsyncSession (+9 more)

### Community 156 - "routing.py"
Cohesion: 0.13
Nodes (13): get_current_user(), Extract user information from the verified token payload. In a real app, this…, FailoverResponse, AsyncSession, BaseModel, UUID, API Routes — Multi-station Routing & Failover, Manually trigger an automatic failover for a scheduled pass. The routing engine… (+5 more)

### Community 167 - "simulate_edge.py"
Cohesion: 0.13
Nodes (20): MissionProfile, Versioned operational profile of a mission., cleanup_previous_run(), get_or_create(), Phase 2.4 â€” End-to-end edge simulation on the dev database. Builds a fresh…, Remove all data from previous simulation runs (dev-demo only)., run(), step() (+12 more)

### Community 169 - "FastAPI"
Cohesion: 0.11
Nodes (24): get_current_user_db(), get_db_session(), AsyncSession, Verify the JWT token from Supabase., Resolve the JWT subject to the persisted User row (Phase 1 tenancy)., verify_token(), health_check(), healthz_check() (+16 more)

## Knowledge Gaps
- **231 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `entrypoint.sh script`, `run.sh script`, `eslintConfig` (+226 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TenantContext` connect `TenantContext` to `EdgeAgentService`, `ObservationJob`, `StationService`, `MissionService`, `business.py`, `OperationsEngine`, `FastAPI`, `services/tenancy.py`, `simulate_edge.py`, `ContactPlanningService`, `.__init__`, `RegulatoryAuthorizationService`, `.__init__`, `test_webhooks.py`, `test_api.py`, `keys.py`, `agent_sim.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `Base` connect `Base` to `EdgeAgentService`, `ObservationJob`, `api_keys.py`, `OperationsEngine`, `ContactPlanningService`, `services/tenancy.py`, `support.py`, `RegulatoryAuthorizationService`, `test_webhooks.py`, `test_sla.py`, `env.py`, `operator.py`, `audit_page`, `pass_console`, `CachedJob`, `agent_sim.py`, `test_agent.py`, `simulate_edge.py`, `DeliveryService`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `ObservationJob` connect `ObservationJob` to `EdgeAgentService`, `routes/data.py`, `DeliveryService`, `simulate_edge.py`, `ContactPlanningService`, `FastAPI`, `test_agent.py`, `CommercialEngine`, `test_sla.py`, `TenantContext`, `Base`, `agent_sim.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `TenantContext` (e.g. with `Organization` and `Role`) actually correct?**
  _`TenantContext` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `ObservationJob` (e.g. with `get_job_details()` and `_job_dict()`) actually correct?**
  _`ObservationJob` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ObservationOrchestrator` (e.g. with `create_job()` and `list_job_events()`) actually correct?**
  _`ObservationOrchestrator` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `.opencode/plugins/graphify.js`, `entrypoint.sh script` to the rest of the system?**
  _231 weakly-connected nodes found - possible documentation gaps or missing edges._