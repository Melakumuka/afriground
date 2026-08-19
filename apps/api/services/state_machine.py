"""
State Machine — shared transition maps and validation for Phase 1 domain objects.
See docs/STATE_MACHINE_SPEC.md.
"""
from typing import Dict, List, Optional

from fastapi import HTTPException


class StateMachine:
    """Validates and applies state transitions from a declarative map."""

    def __init__(self, transitions: Dict[str, List[str]], name: str = "state"):
        self.transitions = transitions
        self.name = name

    def allowed(self, current: str) -> List[str]:
        return self.transitions.get(current, [])

    def can_transition(self, current: str, target: str) -> bool:
        if current == target:
            return False
        return target in self.allowed(current)

    def validate(self, current: str, target: str) -> None:
        if not self.can_transition(current, target):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid {self.name} transition: '{current}' -> '{target}'. "
                    f"Allowed: {self.allowed(current) or 'terminal state'}"
                ),
            )


# ── ObservationJob lifecycle ─────────────────────────────────────────────────

JOB_TRANSITIONS: Dict[str, List[str]] = {
    "DRAFT": ["REQUESTED", "CANCELLED"],
    "REQUESTED": ["VALIDATING", "CANCELLED"],
    "VALIDATING": ["SCHEDULED", "FAILED"],
    "SCHEDULED": ["QUEUED", "CANCELLED"],
    "QUEUED": ["DISPATCHED", "FAILED"],
    "DISPATCHED": ["ACKNOWLEDGED", "FAILED"],
    "ACKNOWLEDGED": ["PREPARING", "FAILED"],
    "PREPARING": ["EXECUTING", "FAILED"],
    "EXECUTING": ["RECEIVING", "PARTIAL_SUCCESS", "FAILED"],
    "RECEIVING": ["PROCESSING", "PARTIAL_SUCCESS", "FAILED"],
    "PROCESSING": ["COMPLETED", "PARTIAL_SUCCESS", "FAILED"],
    "COMPLETED": [],
    "PARTIAL_SUCCESS": [],
    "FAILED": ["QUEUED"],  # bounded retry
    "CANCELLED": [],
}

JOB_TERMINAL_STATES = {"COMPLETED", "PARTIAL_SUCCESS", "FAILED", "CANCELLED"}

# ── Reservation lifecycle ────────────────────────────────────────────────────

RESERVATION_TRANSITIONS: Dict[str, List[str]] = {
    "REQUESTED": ["RESERVED", "CANCELLED", "EXPIRED"],
    "RESERVED": ["CONFIRMED", "CANCELLED", "EXPIRED"],
    "CONFIRMED": ["CANCELLED", "EXPIRED"],
    "CANCELLED": [],
    "EXPIRED": [],
}

# ── ContactOpportunity lifecycle ─────────────────────────────────────────────

CONTACT_OPPORTUNITY_TRANSITIONS: Dict[str, List[str]] = {
    "OPEN": ["RESERVED", "CLOSED", "EXPIRED", "CANCELLED"],
    "RESERVED": ["CLOSED", "CANCELLED", "EXPIRED"],
    "CLOSED": [],
    "EXPIRED": [],
    "CANCELLED": [],
}

# ── Station certification workflow ───────────────────────────────────────────

CERTIFICATION_TRANSITIONS: Dict[str, List[str]] = {
    "REGISTERED": ["PROVISIONING", "REJECTED", "DECERTIFIED"],
    "PROVISIONING": ["VALIDATING", "REJECTED", "DECERTIFIED"],
    "VALIDATING": ["CERTIFIED", "REJECTED", "DECERTIFIED"],
    "CERTIFIED": ["DECERTIFIED"],
    "DECERTIFIED": [],
    "REJECTED": [],
}


JOB_SM = StateMachine(JOB_TRANSITIONS, name="observation job")
RESERVATION_SM = StateMachine(RESERVATION_TRANSITIONS, name="reservation")
CONTACT_OPPORTUNITY_SM = StateMachine(CONTACT_OPPORTUNITY_TRANSITIONS, name="contact opportunity")
CERTIFICATION_SM = StateMachine(CERTIFICATION_TRANSITIONS, name="certification")