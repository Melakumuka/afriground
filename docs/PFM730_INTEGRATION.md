# PFM730 Station Integration Reference

This document captures the technical specifications and integration strategy for the Zodiac PFM730 7.3m antenna system — the primary reference station for AfriGround's Station Gateway.

## 1. Station Overview

The PFM730 is a professional-grade 7.3m Cassegrain antenna system designed for LEO/MEO satellite operations. It is the reference station against which all AfriGround Edge Agent adapters are modeled.

## 2. Station Subsystems

### 2.1 Antenna
- **Reflector:** 7.30m diameter
- **Mount:** 2-axis + tilt pedestal
- **X-band feed:** Cassegrain
- **S-band feed:** Prime focus
- **Polarization:** RHCP / LHCP switchable

### 2.2 Antenna Control Unit (ACU)
- **Modes:** Standby, Ephemeris/TLE, Position, Scan, Auto-track, Stow
- **Supports:** TLE ephemeris loading, satellite presets, elevation masks, azimuth limits
- **Polarization switching:** Controllable
- **Data logging:** TCP/IP, UDP, or serial
- **Safety:** Emergency stop, wind stow interlocks

### 2.3 Antenna Drive Unit (ADU)
- **Components:** Servo Control Unit (SCU/iSCU), motor drives
- **Safety:** Emergency stop button, local control box, physical interlocks

### 2.4 CORTEX HDR (High Data Rate Receiver)
- **Purpose:** Payload data reception
- **Input frequency:** 720 MHz ±190 MHz (or 1.2 GHz ±290 MHz hardware-dependent)
- **Symbol rate:** Up to 320 Msps per channel
- **Modulations:** BPSK, QPSK, OQPSK, UQPSK, 8PSK, GMSK, 16QAM, 16APSK, 32APSK, 64APSK, SOQPSK
- **Decoding:** RS, LDPC, Viterbi, Descrambling, Turbo code 1/2 (CCSDS standard)
- **Frame processing:** Frame sync, CADU/VCDU processing
- **Storage:** 2 TB internal baseline
- **Data outputs:**
  - Data + Clock on ECL
  - Real-time recording to internal disk
  - Real-time TCP/IP output
  - FTP file access

### 2.5 CORTEX CRT (TT&C Unit)
- **Purpose:** Telemetry, Telecommand, Ranging
- **Capabilities:** TM demodulation, TC modulation, Doppler compensation, TM simulation
- **Protocol support:** COP-1, optional SLE (Space Link Emulation)

### 2.6 CORTEX DTR (Digital Tracking Receiver)
- **Purpose:** Auto-track error extraction
- **Tracking:** Coherent and non-coherent modes
- **Output:** Azimuth/elevation tracking errors sent to ACU
- **Calibration:** Parameter management for tracking loop

### 2.7 Mission Control Software (MCS)
- **Primary integration point for AfriGround Edge Agent**
- **Capabilities:**
  - Automated satellite pass scheduling
  - Conflict management
  - Equipment configuration application
  - Ephemeris/TLE loading to ACU
  - Real-time station health monitoring
  - Event severity levels: Info, Warning, Alarm
  - Pass report generation
  - Data export via FTP
- **External interface:** RM/RC (Remote Monitoring / Remote Control)
  - RM: Provides station/equipment status
  - RC: Allows commands and parameter changes
  - ICD reference: STI 200157 MCS-RM/RC Interface Control Document
- **Integration approach:** The Edge Agent acts as an external Satellite Control Centre client to MCS via RM/RC

### 2.8 Time and Frequency
- **Source:** GPS/NTP time server
- **Options:** NTP, IRIG, 10 MHz reference
- **Requirement:** Synchronization mandatory for pass timing and telemetry timestamps

### 2.9 Environment / Safety
- **Sensors:** Wind sensor, weather station
- **Infrastructure:** Radome, de-icing
- **Safety behavior:** Automatic stow when wind limits exceeded
- **Interlocks:** Emergency stop integration

## 3. Integration Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    AfriGround Cloud                              │
│  ┌───────────┐  ┌────────────┐  ┌──────────────┐                │
│  │ Scheduler │  │Orchestrator│  │  Data Store   │                │
│  └─────┬─────┘  └─────┬──────┘  └──────┬───────┘                │
│        └──────────┬────┘               │                         │
│                   │ HTTPS/mTLS         │ MinIO/S3                │
└───────────────────┼────────────────────┼─────────────────────────┘
                    │                    │
     ═══════════════╪════════════════════╪══════  Network Boundary
                    │                    │
┌───────────────────┼────────────────────┼─────────────────────────┐
│ Station Gateway   │                    │                         │
│  ┌────────────────▼───────────────┐    │                         │
│  │       Cloud Client             │    │                         │
│  │  (polls jobs, pushes events)   │    │                         │
│  └────────────────┬───────────────┘    │                         │
│                   │                    │                         │
│  ┌────────────────▼───────────────┐  ┌─▼──────────────────────┐ │
│  │    Job Manager / Executor      │  │   Artifact Uploader    │ │
│  └────────────────┬───────────────┘  └────────────────────────┘ │
│                   │                                              │
│  ┌────────────────▼───────────────┐                              │
│  │  StationGatewayAdapter         │                              │
│  │  (MockZodiacMCS / ZodiacMCS)   │                              │
│  └────────────────┬───────────────┘                              │
│                   │ RM/RC                                        │
│  ┌────────────────▼───────────────┐                              │
│  │     Zodiac PFM730 MCS          │                              │
│  │  ┌─────┐ ┌─────┐ ┌─────┐      │                              │
│  │  │ ACU │ │ HDR │ │ CRT │      │                              │
│  │  └─────┘ └─────┘ └─────┘      │                              │
│  └────────────────────────────────┘                              │
└──────────────────────────────────────────────────────────────────┘
```

## 4. Key Design Rules

1. **MCS is the gateway to hardware.** The Edge Agent NEVER directly controls ACU, HDR, or CRT. It communicates through MCS via RM/RC.
2. **Engineer configures once.** For each satellite, the engineer sets up MCS mission profiles, HDR modem configuration, ACU satellite presets, and RF paths. This is saved as a `StationOperationProfile`.
3. **Edge Agent loads profiles.** For daily passes, the Edge Agent loads the saved profile, updates only the TLE/AOS/LOS/ephemeris, and runs pre-flight checks.
4. **RM/RC ICD required for real integration.** Until STI 200157 is available, the `MockZodiacMCSAdapter` simulates all MCS interactions.
5. **Safety interlocks are physical.** The Edge Agent checks wind, emergency stop, and time sync status, but the physical safety mechanisms (wind stow, E-stop) are part of the ACU/ADU hardware.

## 5. StationOperationProfile Payload Reference

When a station engineer configures a satellite for the first time, the following payloads are captured and stored:

### 5.1 MCS Profile Payload (`mcs_profile_payload`)
```json
{
  "mission_name": "SENTINEL-2A",
  "satellite_preset": "S2A_XBAND",
  "tracking_mode": "ephemeris",
  "pass_scheduling_mode": "automatic",
  "event_logging_level": "all",
  "export_format": "ftp"
}
```

### 5.2 HDR Config Payload (`hdr_config_payload`)
```json
{
  "input_frequency_mhz": 8160.0,
  "symbol_rate_msps": 150.0,
  "modulation": "QPSK",
  "coding": "LDPC_1/2",
  "frame_format": "CCSDS_CADU",
  "descrambling": true,
  "recording": {
    "enabled": true,
    "format": "raw_cadu",
    "realtime_tcp_output": true
  }
}
```

### 5.3 ACU Config Payload (`acu_config_payload`)
```json
{
  "satellite_preset_id": "S2A_XBAND",
  "tracking_mode": "ephemeris",
  "polarization": "RHCP",
  "elevation_mask_deg": 5.0,
  "azimuth_limits": { "min": 0, "max": 540 },
  "auto_track_enabled": true,
  "dtr_feedback": true
}
```

### 5.4 RF Path Payload (`rf_path_payload`)
```json
{
  "band": "X",
  "downlink_frequency_hz": 8160000000,
  "lnb_lo_frequency_hz": 7440000000,
  "if_frequency_mhz": 720.0,
  "polarization": "RHCP",
  "lna_enabled": true,
  "filter_bandwidth_mhz": 40.0
}
```

### 5.5 Decoder Config Payload (`decoder_config_payload`)
```json
{
  "vcid_filter": [0, 1, 5],
  "frame_length_bytes": 1115,
  "rs_interleave": 4,
  "output_format": "cadu",
  "realtime_extraction": true
}
```

## 6. Pre-Flight Checklist Items

Before each pass, the Edge Agent verifies:

| Item | Source | Required |
|---|---|---|
| MCS reachable | RM status query | Yes |
| ACU healthy | RM ACU status | Yes |
| HDR healthy | RM HDR status | Yes |
| Storage sufficient | Local disk check + HDR storage | Yes |
| Time synchronized | GPS/NTP server | Yes |
| Weather safe | Wind sensor < threshold | Yes |
| No emergency stop | ACU/ADU interlock status | Yes |
| Profile loaded | MCS profile selection confirmed | Yes |
| TLE updated | ACU ephemeris upload confirmed | Yes |
| RF path verified | RF chain configuration confirmed | Yes |
| Regulatory valid | Cloud regulatory service | Yes |

## 7. Pass Execution Artifacts

After each pass, these artifacts are collected:

| Artifact | Source | Format |
|---|---|---|
| Pass report | MCS | PDF or structured JSON |
| HDR recording | CORTEX HDR internal disk | Raw CADU / decoded frames |
| ACU tracking log | ACU data logger | CSV or binary |
| Modem lock log | HDR | CSV/JSON (carrier lock, symbol lock, Eb/No) |
| Tracking error log | DTR | CSV (az/el error values) |
| Alarm/event log | MCS | Structured events |
| Weather log | Weather station | CSV (wind, temp, humidity) |

## 8. Execution Receipt Fields

The receipt cryptographically attests to the pass outcome:

- `actual_aos` / `actual_los` — real pass timing
- `carrier_locked` — boolean, was carrier locked during pass
- `symbol_locked` — boolean, was symbol sync achieved
- `recording_started` / `recording_stopped` — timestamps
- `data_volume_bytes` — total recorded data
- `frame_count` — CADU/VCDU frames captured
- `average_ebno` — signal quality metric
- `tracking_error_summary` — max/mean az/el errors
- `time_source` / `clock_offset_ms` — time sync state
- `weather_summary` — wind/conditions during pass
- `pass_report_hash` — SHA-256 of the MCS pass report
- `artifact_manifest_hash` — SHA-256 of the artifact manifest
- `agent_signature` — optional cryptographic signature
