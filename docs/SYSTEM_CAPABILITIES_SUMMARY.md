# AfriGround GSaaS Platform - System Capabilities Summary

**Date:** 2026-08-21
**Target Audience:** Future AI Agents / Principal Engineers taking over the repository.

This document summarizes the current state and capabilities of the AfriGround platform.

## 1. Core Mission & Architecture
AfriGround is a Ground Station Network Operating System (Control Plane). It orchestrates commercial bookings and dispatches jobs to local "Station Gateways" (Edge Agents) installed at physical ground stations. It does **not** directly control hardware; rather, it coordinates with existing Mission Control Software (MCS) via an adapter pattern.

## 2. Backend Capabilities (`apps/api`)
- **FastAPI / SQLAlchemy / Postgres:** The core stack.
- **Orchestration Engine (`services/orchestrator.py`):** Drives `ObservationJob` through a strict state machine (`QUEUED` -> `DISPATCHED` -> `ACKNOWLEDGED` -> `PREPARING` -> `EXECUTING` -> `RECEIVING` -> `PROCESSING` -> `COMPLETED`).
- **Station-Led Configuration (Readiness Gates):** We implemented a critical safety feature where expensive ground hardware is pre-configured by local engineers. The Edge Agent prompts the local engineer for a manual readiness check. The job **cannot** transition to `EXECUTING` until a `StationReadinessEvent` with status `READY` is received from the edge.
- **Commercial Engine (`services/commercial_engine.py`):** Handles Quotes (draft, sent, accepted), Pricing Tiers (standard, premium, enterprise), and Enterprise Contracts (capacity management, SLA tracking).
- **Data Engine & Execution Receipts:** Post-pass, the Edge Agent uploads an `ExecutionReceipt` containing hard telemetry (Eb/No, Lock Status, Data Volume) which the backend processes to finalize the job.

## 3. Frontend Capabilities (`apps/web`)
- **Next.js / Tailwind CSS:** The customer and station owner portal.
- **Job Details / Pass Report UI:** A dedicated page (`/operations/jobs/[job_id]`) that aggregates Job Status, Pre-flight Readiness Checklists, and Post-flight Execution Receipts into a single, beautifully designed pane.
- **Commercial Quotes UI (`/commercial/quotes`):** An interactive pass configurator allowing users to adjust duration and priority to instantly generate and accept quotes based on pricing tiers.
- **Enterprise Contracts UI (`/commercial/contracts/[contract_id]`):** A dashboard featuring a dynamic SVG capacity ring chart, SLA tracking, and remaining contract days.

## 4. Edge Agent (`apps/station-gateway`)
- **Lightweight Local App:** Runs locally at the ground station. Polls the cloud for jobs, surfaces the Readiness Checklist to the local engineer via a simple HTML/Jinja UI, and pushes readiness/receipts back to the cloud.

## 5. Testing & DevOps
- **Test Suite:** Comprehensive pytest suite covering state machines, network routing, webhooks, and regulatory constraints.
- **Local Env:** The local integration tests use a dockerized Postgres instance (`afriground:afriground_dev_password` on port `5433`). 

## 6. Known Gaps / Next Steps
- **Alternative 1: Schedule Injection:** We have designed a plan (`docs/ALTERNATIVE_1_SCHEDULE_INJECTION.md`) for stations that prefer to manage their own task plans instead of Just-In-Time execution. This is designed but not yet implemented.
- **Raw IQ Data Delivery:** The UI shows a button for downloading raw pass data (IQ files), but the actual S3/MinIO pre-signed URL generation and delivery pipeline is pending.
