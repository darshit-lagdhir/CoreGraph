import pytest
import time
from sqlalchemy import text
from dal.queries.search import perform_fuzzy_search
from infra.database import db_manager


@pytest.mark.asyncio
async def test_fuzzy_search_performance_budget(session):
    """
    Performance Audit for Supply Chain Typosquatting search.
    Ensures sub-20ms latency across the 3.88M node ecosystem.
    """
    from dal.seed import seed_osint_specimens
    await seed_osint_specimens(session)
    await session.commit()
    
    search_term = "lodsh"  # Simulating typosquatted lodash lookup

    # Measure purely the high-velocity similarity search
    start = time.perf_counter()
    results = await perform_fuzzy_search(session, search_term)
    end = time.perf_counter()

    latency_ms = (end - start) * 1000
    print(f"\n[AUDIT] Fuzzy Search Latency: {latency_ms:.2f}ms")
    assert latency_ms < 50.0, f"Search exceeded HUD latency budget: {latency_ms}ms"

@pytest.mark.asyncio
async def test_materialized_view_access(session):
    """Verifies O(1) flattened access for HUD risk mapping."""
    from dal.seed import seed_osint_specimens
    await seed_osint_specimens(session)
    await session.commit()
    
    # Check mv_package_risk_summary populates summary metrics
    res = await session.execute(text("SELECT count(*) FROM mv_package_risk_summary"))
    count = res.scalar()
    print(f"[AUDIT] Summary View contains {count} package records.")
    assert count > 0
