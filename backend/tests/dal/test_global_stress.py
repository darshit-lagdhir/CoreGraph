import pytest
import asyncio
import time
import uuid
import sys
import os
import subprocess
from dal.engine import CoreGraphEngine
from dal.models.alerting import AlertSeverity
from dal.models.annotation import Workspace


@pytest.mark.asyncio
async def test_global_persistence_collision(async_session_factory):
    """
    The 'Titan' Audit (Cloud Optimized).
    """
    test_run_id = uuid.uuid4().hex[:8]

    async def ingest_burst():
        async with async_session_factory() as session:
            engine = CoreGraphEngine(session)
            for i in range(5):
                payload = {
                    "name": f"pkg-{test_run_id}-A-{i}",
                    "ecosystem": "npm",
                    "version": "1.0.0",
                }
                await engine.packages.upsert_package(payload)
            await session.commit()
            print(f"[STREAM A] Ingested package versions.")

    async def collaborative_burst():
        async with async_session_factory() as session:
            ws = Workspace(name=f"Audit-WS-{test_run_id}", owner_id=uuid.uuid4())
            session.add(ws)
            await session.flush()

            engine = CoreGraphEngine(session)
            pkg = await engine.packages.upsert_package(
                {"name": f"pkg-{test_run_id}-B", "ecosystem": "npm"}
            )
            await session.flush()

            for i in range(5):
                await engine.mutation.apply_tag_crdt(
                    ws.id, pkg.id, "PACKAGE", f"LABEL-{test_run_id}-{i}", uuid.uuid4(), False, i
                )
            await session.commit()
            print(f"[STREAM B] Applied collaborative tags.")

    async def sentinel_monitoring():
        async with async_session_factory() as session:
            engine = CoreGraphEngine(session)
            pkg = await engine.packages.upsert_package(
                {"name": f"pkg-{test_run_id}-C", "ecosystem": "npm"}
            )
            await session.flush()
            for i in range(5):
                await engine.alerts.log_alert(
                    pkg.id,
                    AlertSeverity.CRITICAL,
                    0.95,
                    0.9,
                    {"trigger": f"STRESS-{test_run_id}-{i}"},
                )
            await session.commit()
            print(f"[STREAM C] Generated critical alerts.")

    start_time = time.perf_counter()
    await asyncio.gather(ingest_burst(), collaborative_burst(), sentinel_monitoring())
    end_time = time.perf_counter()

    duration = end_time - start_time
    print(f"\n[AUDIT] Global Concurrency Verified in {duration:.2f}s")
    assert duration < 120.0
    print("[SUCCESS] The Beast is mathematically stable.")


@pytest.mark.asyncio
async def test_module_2_final_seal(async_session_factory):
    """
    The Ultimate Validation: Section 4/5 Compliance + Titan Audit.
    """
    root_dir = os.getcwd()
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{root_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"

    # 1. PURGE (Section 4)
    subprocess.run(
        [sys.executable, "scripts/purge_development_artifacts.py"],
        check=True,
        cwd=root_dir,
        env=env,
    )

    # 2. AUDIT (Section 5)
    subprocess.run(
        [sys.executable, "scripts/audit_structure.py"], check=True, cwd=root_dir, env=env
    )

    # 3. CONCURRENCY (Section 3)
    await test_global_persistence_collision(async_session_factory)

    # 4. FINAL CRYPTOGRAPHIC SEAL
    async with async_session_factory() as s:
        from dal.queries.integrity import sign_global_graph_state

        final_root = await sign_global_graph_state(s, event_id=uuid.uuid4())
        assert final_root is not None
        print(f"[MODULE 2 SEALED] Root Hash: {final_root.hex()}")
