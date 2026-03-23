import pytest
import time
import uuid
import json
import asyncio
from sqlalchemy import select, func
from dal.models.alerting import AlertEvent, AlertSeverity
from dal.models.graph import Package
from infra.notifier import sentinel


@pytest.fixture(autouse=True)
async def sentinel_cleanup():
    yield
    await sentinel.aclose()


@pytest.mark.asyncio
async def test_alert_latency_budget():
    """
    Verifies that a critical breach triggers a Redis push
    within the 50ms OSINT requirement.
    """
    payload = {
        "type": "TEST_ALERT",
        "package_id": str(uuid.uuid4()),
        "reason": "STRESS_TEST",
        "severity": "CRITICAL",
    }

    start_time = time.perf_counter()
    # 1. Trigger the 'Scream' (Broadcast Path)
    await sentinel.scream(payload)
    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000
    print(f"[AUDIT] Alert Dispatch Latency: {latency_ms:.2f}ms")

    # Validation: Must be sub-50ms across the PCIe bus
    assert latency_ms < 50.0


@pytest.mark.asyncio
async def test_alert_suppression_logic(session):
    """
    Ensures that redundant alerts for the same package are
    suppressed to prevent analyst fatigue.
    """
    # 1. Setup Package and initial state
    pkg = Package(name="signal-monitor", ecosystem="npm")
    session.add(pkg)
    await session.commit()

    # 2. Fire 10 redundant alerts in rapid succession for the same package
    for _ in range(10):
        await sentinel.trigger_and_persist(
            session,
            pkg.id,
            AlertSeverity.CRITICAL,
            risk=0.95,
            criticality=0.88,
            payload={"reason": "velocity_spike"},
        )
    await session.commit()

    # 3. Validation: Only 1 AlertEvent should be persisted in the DB
    stmt = select(func.count(AlertEvent.id)).where(AlertEvent.package_id == pkg.id)
    res = await session.execute(stmt)
    count = res.scalar()

    # Alert suppression ensures only one active CRITICAL alert is tracked until acknowledged
    assert count == 1, f"Suppression failed: {count} alerts persisted instead of 1."
    print("[AUDIT] Alert Suppression Verified.")


@pytest.mark.asyncio
async def test_emergency_vulnerability_escalation(session):
    """
    Verifies that 'Emergency' alerts are isolated for the HUD crisis dashboard.
    """
    pkg = Package(name="crisis-node", ecosystem="pypi")
    session.add(pkg)
    await session.commit()

    # 1. Escalation: Trigger an EMERGENCY alert
    await sentinel.trigger_and_persist(
        session,
        pkg.id,
        AlertSeverity.EMERGENCY,
        risk=1.0,
        criticality=1.0,
        payload={"reason": "CONFIRMED_MALWARE"},
    )
    await session.commit()

    # 2. Query Active Emergencies Index
    # (Matches ix_active_alert_emergencies)
    stmt = select(AlertEvent).where(
        AlertEvent.severity == AlertSeverity.EMERGENCY, AlertEvent.is_acknowledged == False
    )
    res = await session.execute(stmt)
    alert = res.scalars().first()

    assert alert is not None
    assert alert.severity == AlertSeverity.EMERGENCY
    print("[AUDIT] Emergency Escalation Verified.")
