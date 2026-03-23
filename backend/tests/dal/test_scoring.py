import pytest
import time
from sqlalchemy import select, text
import uuid
from dal.models.graph import Package
from dal.models.risk_scoring import RiskScoringIndex, HeatMapGrid
from dal.utils.risk_pipeline import RiskScoringPipeline
from dal.utils.heatmap_aggregator import HeatMapAggregator


@pytest.mark.asyncio
async def test_risk_vector_synthesis_precision(session):
    """
    Verifies that the $R_{idx}$ formula correctly synthesizes
    multiple vectors into a single coherent score.
    """
    pkg = Package(name="target-pkg", ecosystem="cargo")
    session.add(pkg)
    await session.commit()

    # 1. Setup a node with specific high-risk vectors
    # (High Criticality + High Velocity + Poor Telemetry)
    entry = RiskScoringIndex(
        package_id=pkg.id, v_topo=0.9, v_beh=0.8, v_tel=0.2, v_str=0.5, v_temp=0.5
    )
    session.add(entry)
    await session.commit()

    # 2. Trigger the rescore pipeline
    pipeline = RiskScoringPipeline()
    score = await pipeline.calculate_node_risk(session, pkg.id)

    # 3. Validation: Score must be significantly high (~0.6+)
    # (Geometric mean of (0.9, 0.8, 0.5, 0.5, 0.2) weighted (1.0, 1.2, 0.8, 1.0, 0.5))
    print(f"[AUDIT] Calculated R_idx: {score:.4f}")
    assert score > 0.5
    assert score < 1.0

    # 4. Global Recalculate
    await pipeline.batch_rescore_global(session)
    # Check refresh
    await session.refresh(entry)
    assert abs(entry.r_idx - score) < 0.1
    print("[AUDIT] Risk Vector Synthesis Verified.")


@pytest.mark.asyncio
async def test_heatmap_aggregation_throughput(session):
    """
    Ensures that nodes can be aggregated into a
    spatial grid within the 500ms latency budget.
    """
    # 1. Setup Sample Data (1,000 nodes scattered across the grid)
    # Bypassing FK constraints to simulate ecosystem density without 1,000 package rows.
    await session.execute(text("SET session_replication_role = 'replica';"))
    for i in range(1000):
        session.add(
            RiskScoringIndex(id=uuid.uuid4(), package_id=uuid.uuid4(), r_idx=0.5 + (i / 10000.0))
        )
    await session.commit()
    await session.execute(text("SET session_replication_role = 'origin';"))
    await session.commit()

    # 2. Execution: Gridding Sweeper
    aggregator = HeatMapAggregator(session)
    start = time.perf_counter()
    await aggregator.compute_heatmap_grid(grid_res=32)
    end = time.perf_counter()

    latency_ms = (end - start) * 1000
    print(f"[AUDIT] Heat-map accumulation latency: {latency_ms:.2f}ms")

    # 3. Validation: Sub-500ms target for 32^3 grid
    assert latency_ms < 500.0

    # Verify grid population
    hot_cells = await aggregator.get_hot_cells(limit=10)
    assert len(hot_cells) >= 1
    assert hot_cells[0].node_density > 0
    print("[AUDIT] Heat-Map Aggregation Verified.")
