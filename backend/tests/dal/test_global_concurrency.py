import pytest
import asyncio
import time
import uuid
from dal.engine import CoreGraphEngine
from sqlalchemy import text
from dal.models.graph import Package

@pytest.mark.asyncio
async def test_titan_load_concurrency(async_session_factory):
    async def execute_stress_worker(worker_id: int, count: int, run_id: str):
        async with async_session_factory() as session:
            engine = CoreGraphEngine(session)
            results = []
            for i in range(count):
                try:
                    pkg_name = f"titan-pkg-{run_id}-{worker_id}-{i}"
                    pkg = await engine.packages.upsert_package(
                        {"name": pkg_name, "ecosystem": "npm", "version": "1.0.0"}
                    )
                    if i % 20 == 0:
                        dupe = Package(name=pkg_name, ecosystem="npm")
                        session.add(dupe)
                        await session.flush()
                    await session.execute(
                        text("INSERT INTO risk_scoring_index (package_id, r_idx, v_topo, v_beh, v_str, v_temp, v_tel, manual_risk_multiplier) VALUES (:p_id, 0.95, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0)"),
                        {"p_id": pkg.id},
                    )
                    results.append(True)
                except Exception as e:
                    if i <= 2 and worker_id == 0:
                        print(f"Worker Exception [i={i}]: {e}")
                    await session.rollback()
                    results.append(False)
            await session.commit()
            return results

    start = time.perf_counter()
    run_id = str(uuid.uuid4())[:8]
    workers = [execute_stress_worker(w_id, 100, run_id) for w_id in range(100)]
    all_results = await asyncio.gather(*workers)
    
    flat_results = [res for worker_res in all_results for res in worker_res]
    successes = [r for r in flat_results if r is True]
    failures = [r for r in flat_results if r is False]
    
    assert len(failures) >= 500, f"Rollbacks failed: {len(failures)}"
    assert len(successes) >= 9000, f"Successes failed: {len(successes)}"
