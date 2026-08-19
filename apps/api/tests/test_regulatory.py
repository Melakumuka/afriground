from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from models.station_twin import StationCapability, StationLicense, StationCertification
from services.regulatory import RegulatoryAuthorizationService

NOW = datetime.now(timezone.utc)


async def _register_station(session, tenant, code="ZA-TEST-01"):
    svc = RegulatoryAuthorizationService(session, tenant)
    return await svc.register_station(
        code=code,
        name="Test Station",
        country="South Africa",
        latitude=-33.9648,
        longitude=18.6085,
        altitude_m=160.0,
        operator_contact_email="ops@test.local",
    )


async def test_register_station_defaults_safe(session, tenant):
    station = await _register_station(session, tenant)
    assert station.certification_state == "REGISTERED"
    assert station.tx_enabled is False

    cert = (
        await session.execute(
            select(StationCertification).where(StationCertification.station_id == station.id)
        )
    ).scalars().first()
    assert cert is not None
    assert cert.current_state == "REGISTERED"


async def test_register_duplicate_code_rejected(session, tenant):
    await _register_station(session, tenant, code="ZA-TEST-01")
    with pytest.raises(HTTPException) as exc:
        await _register_station(session, tenant, code="ZA-TEST-01")
    assert exc.value.status_code == 409


async def test_certification_transitions(session, tenant):
    station = await _register_station(session, tenant)
    svc = RegulatoryAuthorizationService(session, tenant)

    cert = await svc.transition_certification(station.id, "PROVISIONING", "Provisioning")
    assert cert.current_state == "PROVISIONING"

    cert = await svc.transition_certification(station.id, "VALIDATING", "Validation")
    assert cert.current_state == "VALIDATING"

    cert = await svc.transition_certification(station.id, "CERTIFIED", "Certified")
    assert cert.current_state == "CERTIFIED"
    assert cert.certified_at is not None

    with pytest.raises(HTTPException):
        await svc.transition_certification(station.id, "VALIDATING", "Invalid backwards step")


async def _certify_station(session, tenant, station_id):
    svc = RegulatoryAuthorizationService(session, tenant)
    await svc.transition_certification(station_id, "PROVISIONING", "Provisioning")
    await svc.transition_certification(station_id, "VALIDATING", "Validation")
    await svc.transition_certification(station_id, "CERTIFIED", "Certified")
    station = await session.get(__import__("models.station", fromlist=["GroundStation"]).GroundStation, station_id)
    station.tx_enabled = True
    await session.commit()


async def test_tx_authorization_allows_valid(session, tenant):
    station = await _register_station(session, tenant)
    await _certify_station(session, tenant, station.id)

    session.add(
        StationCapability(
            station_id=station.id, band="UHF",
            frequency_min_hz=430_000_000.0, frequency_max_hz=440_000_000.0,
            max_tx_power_dbm=25.0, tx_authorized=True,
        )
    )
    session.add(
        StationLicense(
            station_id=station.id, license_type="uplink",
            issuing_authority="ICASA", license_number="L1",
            frequency_bands=[{"min_hz": 430_000_000, "max_hz": 440_000_000}],
            max_power_dbm=25.0, issued_at=NOW - timedelta(days=1),
            expires_at=NOW + timedelta(days=30), status="valid",
        )
    )
    await session.commit()

    svc = RegulatoryAuthorizationService(session, tenant)
    result = await svc.evaluate_tx_authorization(station.id, frequency_hz=437_800_000.0, power_dbm=10.0)
    assert result.authorized is True
    assert all(c.passed for c in result.checks)


async def test_tx_authorization_blocks_uncertified(session, tenant):
    station = await _register_station(session, tenant)  # stays REGISTERED
    svc = RegulatoryAuthorizationService(session, tenant)
    result = await svc.evaluate_tx_authorization(station.id, frequency_hz=437_800_000.0, power_dbm=10.0)
    assert result.authorized is False
    check = next(c for c in result.checks if c.rule == "station.certified")
    assert not check.passed


async def test_tx_authorization_blocks_overpower(session, tenant):
    station = await _register_station(session, tenant)
    await _certify_station(session, tenant, station.id)
    session.add(
        StationCapability(
            station_id=station.id, band="UHF",
            frequency_min_hz=430_000_000.0, frequency_max_hz=440_000_000.0,
            max_tx_power_dbm=5.0, tx_authorized=True,
        )
    )
    session.add(
        StationLicense(
            station_id=station.id, license_type="uplink",
            issuing_authority="ICASA", license_number="L2",
            frequency_bands=[{"min_hz": 430_000_000, "max_hz": 440_000_000}],
            max_power_dbm=5.0, issued_at=NOW - timedelta(days=1),
            expires_at=NOW + timedelta(days=30), status="valid",
        )
    )
    await session.commit()

    svc = RegulatoryAuthorizationService(session, tenant)
    result = await svc.evaluate_tx_authorization(station.id, frequency_hz=437_800_000.0, power_dbm=20.0)
    assert result.authorized is False
    assert not next(c for c in result.checks if c.rule == "power.limit").passed