# STATE_MACHINE_SPEC.md

## ObservationJob lifecycle

```
DRAFT ──▶ REQUESTED ──▶ VALIDATING ──▶ SCHEDULED ──▶ QUEUED ──▶ DISPATCHED ──▶ ACKNOWLEDGED
                                          │                             │
                                          ▼                             ▼
                                       FAILED                        PREPARING
                                                                         │
                                                                         ▼
                                                                    EXECUTING
                                                                         │
                                                                         ▼
                                                                    RECEIVING
                                                                         │
                                                                         ▼
                                                                    PROCESSING
                                                                         │
                              ┌──────────────┬──────────────┬───────────┤
                              ▼              ▼              ▼
                         COMPLETED     PARTIAL_SUCCESS    FAILED
```

Terminal: `COMPLETED`, `PARTIAL_SUCCESS`, `FAILED`, `CANCELLED`.
Retry: `FAILED → QUEUED` is allowed (bounded by `retry_count`/`max_retries`).

Transitions are enforced by `services/state_machine.py` and recorded in `job_events`
(from_state → to_state, actor, reason). All transitions are idempotent-gaurded: a no-op
transition (same state) is rejected.

## Reservation lifecycle

`REQUESTED → RESERVED → CONFIRMED → CANCELLED | EXPIRED`
(from `RESERVED` and `CONFIRMED` a reservation may also transition to `CANCELLED`).

## ContactOpportunity lifecycle

`OPEN → RESERVED → CLOSED | EXPIRED | CANCELLED`

## Certification workflow (StationCertification)

```
REGISTERED ──▶ PROVISIONING ──▶ VALIDATING ──▶ CERTIFIED ──▶ DECERTIFIED
                  │                 │
                  ▼                 ▼
               REJECTED          REJECTED
```

Every transition writes a `station_certification_events` row (auditable trail).

## Incident lifecycle (legacy, kept)

`open → investigating → identified → resolved → closed` (with reopen `resolved → investigating`).