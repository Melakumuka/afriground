# Alternative 1: Schedule Injection Architecture

## Overview
This document outlines the implementation plan for transitioning the AfriGround Edge Agent to a "Schedule Injection" (Alternative 1) model. In this model, the Cloud orchestrator acts as a booking engine, and the Edge Agent acts as a schedule synchronizer. The local ground station's Mission Control Software (e.g., Zodiac PFM730 MCS) becomes the master task planner for daily execution.

## Core Principles
1. **Daily Schedule Synchronization:** The Edge Agent polls the cloud for the daily or weekly schedule of assigned `ObservationJob`s.
2. **Format Translation:** The Edge Agent translates the cloud's job list (AOS, LOS, Satellite ID, Profile ID) into the proprietary task plan format expected by the local MCS.
3. **Local Autonomy:** Once the schedule and updated TLEs are injected into the MCS, the local hardware executes the passes automatically based on the schedule, even if internet connectivity is lost.
4. **Asynchronous Reporting:** Pass reports and artifacts are collected by the Edge Agent after the MCS finishes a pass and uploaded to the cloud when connectivity permits.

## Implementation Steps

### 1. Cloud API Updates (`apps/api`)
- **Schedule Endpoint:** Create `GET /api/v1/edge/stations/{station_id}/schedule` which returns a time-windowed list of all `CONFIRMED` jobs for the station, rather than just the "next" job.
- **Job States:** Ensure the `JOB_SM` state machine supports an `INJECTED` or `SCHEDULED_LOCALLY` state, indicating the job has been handed off to the local MCS.

### 2. Edge Agent Updates (`apps/station-gateway`)
- **Schedule Sync Worker:** Modify `worker.py` to pull the daily schedule instead of just "dispatched" jobs.
- **Adapter Interface Changes:**
  - Remove just-in-time commands like `load_mcs_profile()` and `start_pass_recording()`.
  - Add `inject_daily_schedule(schedule_payload)`.
  - Add `sync_tles(tle_list)`.
- **Zodiac MCS Adapter Implementation:**
  - Implement the translation logic that converts AfriGround's JSON schedule into the Zodiac MCS XML or database schedule format via the RM/RC interface.
- **Reconciliation Worker:** 
  - Add a worker that periodically queries the MCS for completed passes in its internal schedule. When a pass completes, it generates the `ExecutionReceipt` and uploads the artifacts.

### 3. Transition Strategy
- **Hybrid Support:** The Edge Agent can support both modes via a configuration flag (`AGENT_EXECUTION_MODE = JIT | SCHEDULE_INJECTION`). This allows legacy stations to use JIT, while advanced stations like the PFM730 use Schedule Injection.
- **Conflict Resolution:** If a pass is cancelled in the cloud, the Edge Agent must send a targeted DELETE command to the local MCS schedule to remove the task before it executes.
