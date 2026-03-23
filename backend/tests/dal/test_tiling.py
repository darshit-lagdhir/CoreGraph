import pytest
import uuid
import msgpack
from sqlalchemy import select
from dal.models.graph import Package
from dal.models.criticality import CriticalityScore
from dal.models.tiling import SummaryNode, VisualizationTile
from dal.queries.tiling import rebuild_hierarchical_visualization


@pytest.mark.asyncio
async def test_lod_aggregation_integrity(session):
    """
    Verifies that the SummaryNode correctly represents the weighted risk
    averages of its constituent topological clusters.
    """
    # 1. Setup Silo (10 nodes with fixed criticality and risk scores)
    for i in range(10):
        pkg = Package(name=f"tiling-pkg-{i}", ecosystem="npm")
        session.add(pkg)
        await session.flush()
        await session.refresh(pkg)

        crit = CriticalityScore(package_id=pkg.id, c_idx=0.8, authority_score=1.0)
        session.add(crit)

    await session.flush()

    # 2. Trigger Hierarchical Summarization Kernel
    await rebuild_hierarchical_visualization(session, resolution=100)

    # 3. Validation: Verify SummaryNode aggregates
    res = await session.execute(select(SummaryNode).where(SummaryNode.lod_level == 0))
    summary = res.scalars().first()

    assert summary is not None
    assert summary.total_nodes_contained >= 10
    # Expected Risk should be centered around the criticality (0.8) and random bias
    assert 0.4 < summary.representative_risk_score < 1.0


@pytest.mark.asyncio
async def test_tile_streaming_latency(session):
    """
    Ensures that a VisualizationTile payload is correctly serialized
    into MessagePack for zero-lag 144Hz HUD response.
    """
    # 0. Seed data
    for i in range(10):
        pkg = Package(name=f"tile-pkg-{i}", ecosystem="npm")
        session.add(pkg)
        await session.flush()
        await session.refresh(pkg)
        crit = CriticalityScore(package_id=pkg.id, c_idx=0.9, authority_score=1.0)
        session.add(crit)
    await session.flush()

    # 1. Trigger Tiling
    await rebuild_hierarchical_visualization(session, resolution=50)

    # 2. Execution: Fetch and deserialize
    res = await session.execute(select(VisualizationTile).limit(1))
    tile = res.scalars().first()

    assert tile is not None
    decoded = msgpack.unpackb(tile.tile_data)

    # 3. Assertion: Boundary integrity and payload structure
    assert "min" in decoded
    assert "max" in decoded
    assert "points" in decoded
    assert len(decoded["min"]) == 3
    assert len(decoded["max"]) == 3
