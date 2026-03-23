import pytest
import uuid
from datetime import datetime, timedelta, timezone
from dal.models.graph import Package
from dal.models.temporal import NodeDelta
from dal.repositories.temporal_repo import TemporalRepository

@pytest.mark.asyncio
async def test_temporal_existence_range(session):
    t_base = datetime.now(timezone.utc)
    t_start = t_base - timedelta(hours=1)
    t_end = t_base + timedelta(hours=1)
    pkg_name = f"temporal-audit-{uuid.uuid4().hex[:6]}"

    pkg = Package(name=pkg_name, ecosystem="npm", valid_from=t_start, valid_to=t_end)
    session.add(pkg)
    await session.commit()

    repo = TemporalRepository(session)
    res = await repo.get_package_at_time(pkg_name, t_base)
    assert res is not None

    res_future = await repo.get_package_at_time(pkg_name, t_base + timedelta(hours=5))
    assert res_future is None

@pytest.mark.asyncio
async def test_delta_persistence(session):
    repo = TemporalRepository(session)
    snap = await repo.create_snapshot(f"snap-{uuid.uuid4().hex[:4]}")

    id_pkg = uuid.uuid4()
    await repo.record_node_delta(
        snap.id, id_pkg, "UPDATED", {"risk_score": {"old": 0.1, "new": 0.9}}
    )
    await session.commit()
    
    from sqlalchemy import select
    res = await session.execute(select(NodeDelta).where(NodeDelta.snapshot_id == snap.id))
    delta = res.scalars().first()
    assert delta is not None
    assert delta.change_type == "UPDATED"
    assert delta.diff_payload["risk_score"]["new"] == 0.9
