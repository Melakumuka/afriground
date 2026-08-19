# REGULATORY_RULES.md

## Safety defaults

- Every newly registered station: `tx_enabled = false`, `certification_state = 'REGISTERED'`.
- Uplink is **denied** unless every check in `evaluate_tx_authorization` passes.

## TX authorization checks (all must pass)

1. **Station identity** — station exists.
2. **Certification** — `StationCertification.current_state == 'CERTIFIED'`.
3. **TX switch** — `GroundStation.tx_enabled == true`.
4. **License validity** — an active `StationLicense` exists for the station, is not expired/suspended/revoked,
   and authorizes the requested band + issuing country.
5. **Frequency authorization** — requested frequency falls within a licensed band **and** within a
   `StationCapability` band (frequency_min_hz ≤ f ≤ frequency_max_hz).
6. **Power limit** — requested EIRP/power ≤ min(license.max_power_dbm, capability.max_tx_power_dbm).
7. **Mission profile** — `MissionRFProfile.is_uplink_enabled == true` and the requested frequency
   matches the profile's uplink frequency.

## Geographic / coordination notes

- Each station carries a `country` and the licenses record the issuing authority + country.
- Frequency coordination is assumed handled at license time; the platform enforces the license
  artifact, not ITU coordination.

## Audit

All TX decisions are persisted via `OutboxEvent` (`REGULATORY.TX_CHECK`) with the full check result
payload for traceability.

## Implementation

- `services/regulatory.py` — `RegulatoryAuthorizationService` + `RegulatoryCheckResult` (Pydantic)
  with per-rule pass/fail and a composite `authorized` boolean.