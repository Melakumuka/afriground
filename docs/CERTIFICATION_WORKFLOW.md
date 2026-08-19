# CERTIFICATION_WORKFLOW.md

## States

`REGISTERED → PROVISIONING → VALIDATING → CERTIFIED` (→ `DECERTIFIED`), or `REJECTED` at any
pre-certification step.

## Flow

1. **REGISTERED** — station created by the operator. `tx_enabled` is **false** by default. Hardware
   and capabilities are attached (StationHardware, StationCapability).
2. **PROVISIONING** — operator configures antennas/SDRs, submits hardware inventory, and completes
   commissioning checks (time sync enabled, agent identity provisioned).
3. **VALIDATING** — platform reviews RF capabilities against the operator's licenses, verifies
   frequency authorization, and runs automated compatibility checks. A `RegulatoryAuthorizationService`
   review is recorded (`station_certification_events`).
4. **CERTIFIED** — station may accept reserved contacts. `tx_enabled` remains **false** until the
   operator explicitly enables transmission and a regulatory TX check passes per-contact.
5. **DECERTIFIED** — certification revoked (license expiry, safety incident). Jobs must not be
   scheduled against a decertified station.

## Enforced invariants

- A station can only host contacts once `CERTIFIED`.
- A station can only transmit when `tx_enabled = true` **and** the per-contact
  `RegulatoryAuthorizationService.evaluate_tx_authorization(...)` passes.
- Every transition is logged in `station_certification_events` with actor + reason + timestamps.

## Implementation

- `services/regulatory.py` — `RegulatoryAuthorizationService`
  - `register_station(...)` → creates station + certification `REGISTERED` + event.
  - `transition_certification(...)` — validates workflow, writes event.
  - `evaluate_tx_authorization(...)` — composite TX safety gate.
- `StationCertification` tracks the current state; `StationCertificationEvent` the history.