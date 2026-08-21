# Frontend Integration Plan: Exposing Backend Features

This document outlines the implementation plan for exposing the powerful backend logic we have built (Readiness Events, Execution Receipts) to the user via the AfriGround Next.js frontend.

## 1. Goal
Provide a "Pass Report" (or Job Details) view in the web portal so that Satellite Operators (Customers) and Station Owners can see the real-time lifecycle of an `ObservationJob`. Specifically:
- **Pre-flight:** See if the station engineer has confirmed the readiness checklist (`StationReadinessEvent`).
- **Post-flight:** See the telemetry metrics and data volume generated during the pass (`ExecutionReceipt`).

## 2. API Updates (`apps/api`)
We need a dedicated endpoint to fetch the aggregated state of an Observation Job, including its pre-flight and post-flight metadata.

- **Create Endpoint:** `GET /api/v1/operations/jobs/{job_id}`
- **Response Payload:**
  - Core job details (AOS, LOS, Status, Satellite).
  - `readiness_event`: { status, confirmed_at, checklist_results }
  - `receipt`: { carrier_locked, ebno, data_volume_bytes, pass_report_hash }

## 3. Frontend Updates (`apps/web`)

### 3.1 Job Details Page
Create a new Next.js page: `apps/web/src/app/[locale]/operations/jobs/[job_id]/page.tsx`
This page will contain three primary UI cards:
1. **Job Overview:** Basic pass metadata and current state machine status.
2. **Pre-flight Readiness:** A card showing the Station Engineer's checklist (e.g., "MCS Profile Loaded: ✅", "Weather Safe: ✅").
3. **Execution Receipt (Pass Report):** A card that appears only when the job is `COMPLETED`, displaying the collected telemetry (Eb/No, lock status, data volume) and a mock button to "Download .raw IQ Data".

### 3.2 Navigation Hooks
Update existing tables (e.g., in the booking or operations dashboard) to make the Job IDs clickable, routing the user to the new Job Details page.
