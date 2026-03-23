import pytest
import uuid
from sqlalchemy import select, text
from dal.models.graph import Package, PackageVersion, DependencyEdge
from dal.models.telemetry import HealthAnomaly, NodeTelemetry
from dal.utils.sweeper import ConsistencySweeper
from dal.queries.telemetry import compute_node_vitality_score


@pytest.mark.asyncio
async def test_metadata_void_detection(session):
    """
    Verifies that the Consistency Sweeper identifies a package
    with missing critical metadata (e.g. version_latest).
    """
    # 1. Setup Silo (Incomplete package)
    pkg = Package(name="orphan-package", ecosystem="npm", version_latest=None)
    session.add(pkg)
    await session.commit()

    # 2. Trigger Autonomous Sweeper
    sweeper = ConsistencySweeper(session)
    count = await sweeper.audit_dag_structure()

    # Validation: Anomaly must be flagged as METADATA_VOID
    assert count >= 1
    res = await session.execute(
        select(HealthAnomaly)
        .where(HealthAnomaly.anomaly_type == "METADATA_VOID")
        .order_by(HealthAnomaly.detected_at.desc())
    )
    anomaly = res.scalars().first()
    assert anomaly is not None
    assert anomaly.details["missing_field"] == "version_latest"


@pytest.mark.asyncio
async def test_vitality_score_quantization(session):
    """
    Asserts that the Vitality Score ($\mathcal{V}_n$) correctly penalizes
    nodes with missing versions or ecosystem metadata.
    """
    # 1. Setup incomplete node (Missing Versions / Metadata)
    pkg = Package(name="incomplete-pkg", ecosystem="incomplete")
    session.add(pkg)
    await session.flush()
    await session.refresh(pkg)

    # 2. Execution: Calculate Vitality
    v_n = await compute_node_vitality_score(session, package_id=pkg.id)

    # 3. Validation: Score MUST be penalized (Metadata=0.6, Structural=0.0)
    # 0.4*0.6 + 0.4*0.0 + 0.2*1.0 = 0.24 + 0.2 = 0.44
    assert v_n < 0.5

    # 4. Check Telemetry persistence
    res = await session.execute(select(NodeTelemetry).where(NodeTelemetry.package_id == pkg.id))
    tel = res.scalars().first()
    assert tel.is_structurally_sound == 0
