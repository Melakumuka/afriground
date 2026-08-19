import pytest
from fastapi import HTTPException

from services.state_machine import (
    JOB_SM,
    RESERVATION_SM,
    CONTACT_OPPORTUNITY_SM,
    CERTIFICATION_SM,
    JOB_TERMINAL_STATES,
)


def test_job_happy_path_transitions():
    path = ["DRAFT", "REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED", "DISPATCHED",
            "ACKNOWLEDGED", "PREPARING", "EXECUTING", "RECEIVING", "PROCESSING", "COMPLETED"]
    for current, nxt in zip(path, path[1:]):
        assert JOB_SM.can_transition(current, nxt), f"{current} -> {nxt}"


def test_job_invalid_transition_rejected():
    with pytest.raises(HTTPException) as exc:
        JOB_SM.validate("DRAFT", "COMPLETED")
    assert exc.value.status_code == 400


def test_terminal_states_are_absorbing():
    # FAILED is terminal except for its bounded retry edge to QUEUED.
    for terminal in ["COMPLETED", "PARTIAL_SUCCESS", "CANCELLED"]:
        assert JOB_SM.allowed(terminal) == []
        with pytest.raises(HTTPException):
            JOB_SM.validate(terminal, "DRAFT")


def test_job_failed_allows_bounded_retry():
    assert JOB_SM.can_transition("FAILED", "QUEUED")


def test_reservation_lifecycle():
    assert RESERVATION_SM.can_transition("REQUESTED", "RESERVED")
    assert RESERVATION_SM.can_transition("RESERVED", "CONFIRMED")
    assert RESERVATION_SM.can_transition("CONFIRMED", "CANCELLED")
    with pytest.raises(HTTPException):
        RESERVATION_SM.validate("REQUESTED", "CONFIRMED")


def test_contact_opportunity_lifecycle():
    assert CONTACT_OPPORTUNITY_SM.can_transition("OPEN", "RESERVED")
    assert CONTACT_OPPORTUNITY_SM.can_transition("RESERVED", "CLOSED")
    with pytest.raises(HTTPException):
        CONTACT_OPPORTUNITY_SM.validate("CLOSED", "RESERVED")


def test_certification_workflow():
    path = ["REGISTERED", "PROVISIONING", "VALIDATING", "CERTIFIED"]
    for current, nxt in zip(path, path[1:]):
        assert CERTIFICATION_SM.can_transition(current, nxt)
    with pytest.raises(HTTPException):
        CERTIFICATION_SM.validate("REGISTERED", "CERTIFIED")
    with pytest.raises(HTTPException):
        CERTIFICATION_SM.validate("DECERTIFIED", "VALIDATING")


def test_no_self_transition():
    assert not JOB_SM.can_transition("DRAFT", "DRAFT")
    assert not CERTIFICATION_SM.can_transition("CERTIFIED", "CERTIFIED")