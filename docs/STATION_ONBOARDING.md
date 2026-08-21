# Station Onboarding Workflow

This document describes the complete onboarding lifecycle for a new ground station and its satellite profiles in AfriGround.

**Core principle:** The station comes first. Local engineers configure their own expensive equipment. AfriGround orchestrates the commercial layer on top.

## 1. Station Registration & Installation

### 1.1 Station Registration (Cloud Side)
1. Station operator creates an Organization/Tenant account on AfriGround.
2. Station operator registers their ground station:
   - Name, location (lat/lon/alt), country
   - Antenna specifications (diameter, mount type, bands)
   - Contact information
3. Station enters `REGISTERED` state.

### 1.2 Edge Agent Installation (Station Side)
1. AfriGround provides the Station Gateway software package.
2. Station IT installs the Edge Agent (`apps/station-gateway`) on the station's local network.
3. Edge Agent is configured with:
   - Station ID
   - Cloud API URL
   - Authentication credentials (mTLS certificates or short-lived tokens)
   - Local MCS adapter selection (e.g., `mock_zodiac_mcs` or `zodiac_mcs`)
4. Edge Agent starts and sends its first heartbeat to the cloud.
5. Cloud creates a `StationAgentIdentity` record.

### 1.3 Capability Registration
The station engineer registers the station's capabilities through the Edge Agent local UI:
- Supported bands (S, X, Ku, Ka)
- Frequency ranges per band
- Supported modulations and symbol rates
- Antenna size and gain
- RX/TX capability
- Data recording capability
- Time synchronization source and quality
- Regulatory licenses (uploaded documents)

These are stored as `StationCapability`, `StationHardware`, and `StationLicense` records in the cloud.

### 1.4 Integration Testing
1. Edge Agent runs automated health checks:
   - MCS connectivity (via adapter RM interface)
   - ACU status reporting
   - HDR status reporting
   - Time sync verification
   - Storage capacity check
   - Weather sensor connectivity
2. Results reported to cloud.
3. Station transitions to `PROVISIONING` → `VALIDATING`.

### 1.5 Station Certification
1. AfriGround reviews the station's capabilities, licenses, and test results.
2. Station transitions to `CERTIFIED` — now available in the commercial marketplace.
3. A `StationCertificationEvent` is recorded for audit.

---

## 2. Satellite Profile Onboarding (Configure Once)

This is the critical "station-first" workflow. The local engineer configures their equipment for a specific satellite **once**. This configuration is saved and reused for every future pass.

### 2.1 Mission Profile Arrives
A satellite operator submits a Mission Profile to AfriGround Cloud, containing:
- Spacecraft identity (NORAD ID, name)
- Downlink frequency, bandwidth, modulation, symbol rate, coding, frame format
- Uplink parameters (if applicable)
- Polarization
- Telemetry/telecommand definitions
- Operational constraints (min elevation, blackout windows)
- SLA requirements

### 2.2 Station Engineer Configures Equipment
The station engineer uses their local tools to configure the physical equipment:

#### MCS Configuration
- Create a new mission/satellite preset in the Zodiac MCS
- Define pass scheduling parameters
- Configure event logging and export settings

#### HDR Modem Configuration
- Set input frequency (IF after LNB downconversion)
- Set symbol rate, modulation, coding
- Configure frame format (CCSDS CADU/VCDU)
- Enable descrambling if required
- Configure recording mode and real-time output

#### ACU Configuration
- Create satellite preset with:
  - Tracking mode (ephemeris/auto-track)
  - Polarization (RHCP/LHCP)
  - Elevation mask
  - Azimuth limits
- Load initial TLE for testing

#### RF Path Configuration
- Select antenna feed (X-band Cassegrain or S-band prime focus)
- Configure LNB/LNA chain
- Set IF frequency and filter bandwidth
- Verify RF path continuity

#### Decoder/Output Configuration
- Set VCID filters
- Configure frame extraction
- Set output format and delivery method

### 2.3 Save Station Operation Profile
Once configuration is complete and verified, the engineer saves it through the Edge Agent local UI:

1. The Edge Agent collects all configuration payloads:
   - `mcs_profile_payload` — MCS mission/preset settings
   - `hdr_config_payload` — HDR modem parameters
   - `acu_config_payload` — ACU satellite preset
   - `rf_path_payload` — RF chain configuration
   - `decoder_config_payload` — Frame processing settings
   - `safety_payload` — Wind limits, timeout thresholds

2. A `StationOperationProfile` is created with:
   - `station_id` + `mission_profile_id` + `satellite_id`
   - `certification_state = CONFIGURING`
   - `operation_mode = MANUAL_CONFIRMED` (default for PFM730)

3. The profile is synced to AfriGround Cloud.

### 2.4 Qualification Testing
1. A test pass (real or simulated) is executed using the saved profile.
2. The engineer verifies:
   - Antenna tracks correctly
   - HDR achieves carrier and symbol lock
   - Data is recorded successfully
   - Frames are decoded correctly
   - Artifacts are collected and uploadable
3. Profile transitions: `CONFIGURING` → `TESTING` → `QUALIFICATION_PASSED`.

### 2.5 Profile Certification
1. AfriGround (or the station operator) certifies the profile.
2. Profile transitions to `CERTIFIED`.
3. The satellite is now commercially bookable at this station.

---

## 3. Normal Pass Workflow (Execute Many)

After the profile is certified, recurring passes follow a streamlined workflow:

### 3.1 Booking → Job Creation (Cloud)
1. Satellite operator requests a contact through AfriGround.
2. Cloud checks: capability match, station certification, profile certification, regulatory authorization, availability, conflicts, pricing.
3. Cloud creates: `ContactOpportunity` → `Reservation` → `ScheduledContact` → `ObservationJob`.

### 3.2 Job Assignment (Cloud → Edge)
1. Edge Agent polls `GET /api/v1/edge/jobs/assigned`.
2. Edge Agent receives the job with the `station_operation_profile_id`.
3. Edge Agent loads the saved `StationOperationProfile` from local cache.
4. Edge Agent acknowledges the job.

### 3.3 Pass Preparation (Edge)
1. Edge Agent updates pass-specific data:
   - Fresh TLE → loaded into ACU via adapter
   - AOS/LOS times
   - Expected Doppler parameters
2. Edge Agent runs pre-flight checks (via adapter `run_preflight_checks()`):
   - MCS reachable ✓
   - ACU healthy ✓
   - HDR healthy ✓
   - Storage sufficient ✓
   - Time synchronized ✓
   - Weather safe ✓
   - No emergency stop ✓
   - Profile loaded ✓
   - TLE updated ✓
   - RF path verified ✓

### 3.4 Readiness Confirmation (Edge — Engineer)
1. Edge Agent displays the Pass Console to the station engineer.
2. Engineer reviews:
   - Job details (satellite, AOS/LOS, frequency)
   - Loaded profile summary
   - Pre-flight check results
   - Checklist items
3. Engineer clicks **CONFIRM READY** (or **NOT READY** with reason).
4. Edge Agent sends `POST /api/v1/edge/jobs/{job_id}/readiness` to cloud.
5. Cloud records `StationReadinessEvent` and updates `ObservationJob.readiness_status`.
6. **Orchestrator gate:** Job cannot transition to `EXECUTING` without `READY` status.

### 3.5 Pass Execution (Edge → Station Equipment)
1. Edge Agent instructs MCS to begin pass via adapter.
2. Station equipment executes autonomously:
   - ACU tracks satellite using loaded TLE
   - HDR acquires carrier, achieves symbol lock
   - Data is recorded to HDR internal storage
   - DTR provides tracking error feedback to ACU
   - CRT handles TM/TC if applicable
3. Edge Agent monitors pass status via adapter:
   - Tracking quality
   - Carrier/symbol lock status
   - Recording state
   - Alarms and events

### 3.6 Post-Pass (Edge)
1. Edge Agent collects artifacts via adapter:
   - MCS pass report
   - HDR recorded data
   - ACU tracking log
   - Modem lock log
   - Event/alarm log
   - Weather log
2. Edge Agent calculates checksums for all artifacts.
3. Edge Agent generates `ExecutionReceipt`:
   - Actual AOS/LOS, lock status, data volume, frame count, Eb/No, tracking errors
   - Hash of pass report + artifact manifest
   - Optional agent signature
4. Edge Agent uploads receipt to cloud: `POST /api/v1/edge/receipts`.
5. Edge Agent uploads artifacts using resumable upload.

### 3.7 Data Delivery (Cloud)
1. Cloud stores receipt and artifacts in MinIO/S3.
2. Cloud delivers data products to the satellite operator.
3. Cloud finalizes usage metering and billing.
4. Cloud records audit trail.

---

## 4. Operation Modes

| Mode | Engineer Action | Use Case |
|---|---|---|
| `MANUAL_CONFIRMED` | Engineer must click CONFIRM READY before every pass | Default for PFM730 and other expensive stations |
| `SEMI_AUTOMATIC` | Engineer reviews but auto-confirms if all checks pass | Stations with high reliability and simple operations |
| `AUTOMATIC` | No engineer confirmation required | Fully automated stations (e.g., SatNOGS) |

## 5. Profile Lifecycle States

```
CONFIGURING → TESTING → QUALIFICATION_PASSED → CERTIFIED → SUSPENDED → RETIRED
                 ↓                                  ↓
              FAILED                            DECERTIFIED
```

- `CONFIGURING`: Engineer is setting up equipment
- `TESTING`: Configuration saved, test pass in progress
- `QUALIFICATION_PASSED`: Test pass succeeded
- `CERTIFIED`: Profile approved for commercial operations
- `SUSPENDED`: Temporarily unavailable (maintenance, issue)
- `RETIRED`: No longer in use
