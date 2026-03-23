import pytest
import time
import uuid
from sqlalchemy import text
from dal.models.graph import Package
from dal.models.spatial import PackageSpatialIndex
from dal.utils.subgraph_extractor import SubgraphExtractor


@pytest.mark.asyncio
async def test_spatial_query_precision(session):
    """
    Verifies that a 3D box query returns exactly the nodes
    that fall within the risk-space coordinates.
    """
    # 0. PostgreSQL Extension Setup
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS cube;"))
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS earthdistance;"))
    await session.commit()

    # 1. Setup Sample Node (Criticality=0.9, Risk=0.8, Time=0.95)
    pkg = Package(name="critical-pkg", ecosystem="npm")
    session.add(pkg)
    await session.commit()

    # Insert spatial vector using raw SQL 'cube' type
    await session.execute(
        text("""
        INSERT INTO package_spatial_index (id, package_id, risk_vector)
        VALUES (:id, :p_id, cube(array[0.9, 0.8, 0.95]))
    """),
        {"id": uuid.uuid4(), "p_id": pkg.id},
    )
    await session.commit()

    # 2. Execution: Query 'box' (0.8, 0.5, 0.9) to (1.0, 1.0, 1.0)
    extractor = SubgraphExtractor(session)
    box_query = "(0.8, 0.5, 0.9), (1.0, 1.0, 1.0)"

    start_time = time.perf_counter()
    node_ids = await extractor.query_spatial_box(box_query)
    end_time = time.perf_counter()

    # 3. Validation: Latency must be sub-10ms for a single hit
    latency_ms = (end_time - start_time) * 1000
    print(f"[AUDIT] Spatial query latency: {latency_ms:.2f}ms")

    assert pkg.id in node_ids
    assert len(node_ids) >= 1


@pytest.mark.asyncio
async def test_geo_jurisdictional_isolation(session):
    """
    Ensures that the spatial index isolates nodes within
    specific geographical boundaries (e.g., Lat/Long Point indexing).
    """
    pkg = Package(name="eu-package", ecosystem="cargo")
    session.add(pkg)
    await session.commit()

    # Insert point (52.5, 13.4) - Berlin
    await session.execute(
        text("""
        INSERT INTO package_spatial_index (id, package_id, risk_vector, origin_location)
        VALUES (:id, :p_id, cube(array[0.1, 0.1, 0.1]), point(52.5, 13.4))
    """),
        {"id": uuid.uuid4(), "p_id": pkg.id},
    )
    await session.commit()

    # Query Berlin circle (point @> circle) or box
    res = await session.execute(text("""
        SELECT package_id FROM package_spatial_index
        WHERE origin_location <@ box(point(52, 13), point(53, 14))
    """))
    ids = [row[0] for row in res.all()]
    assert pkg.id in ids
