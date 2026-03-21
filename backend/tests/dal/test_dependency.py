import pytest
import uuid
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from dal.base import Base
from dal.models.package import Package
from dal.models.version import PackageVersion
from dal.models.dependency import DependencyEdge
from dal.queries.traversal import get_blast_radius
from core.config import settings


@pytest.fixture
async def engine():
    engine = create_async_engine(settings.DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest.fixture
def async_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db(engine):
    """Create isolated PostgreSQL environment for architectural verification."""
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS dependency_edges CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS package_versions CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS packages CASCADE;"))

        # Enable pg_trgm for GIN Index
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

        await conn.run_sync(Base.metadata.create_all)
    return


@pytest.fixture
async def session(async_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Provides a fresh asynchronous session for each test."""
    async with async_session_factory() as sess:
        yield sess


@pytest.mark.asyncio
async def test_blast_radius_recursion_limit(session: AsyncSession):
    """Assertion 1: Depth guard prevents infinite loops in circular dependency cycles."""
    # Create nodes: pkg_c -> pkg_b -> pkg_a -> pkg_c (cycle)
    pkgs = [Package(ecosystem="npm", name=f"pkg_{i}") for i in "abc"]
    session.add_all(pkgs)
    await session.commit()
    for p in pkgs:
        await session.refresh(p)

    # Create versions
    vers = [
        PackageVersion(package_id=p.id, version_string="1.0.0", semver_sort_index=100) for p in pkgs
    ]
    session.add_all(vers)
    await session.commit()
    for v in vers:
        await session.refresh(v)

    # Create cycle: v_a -> pkg_b, v_b -> pkg_c, v_c -> pkg_a
    edges = [
        DependencyEdge(
            parent_version_id=vers[0].id, child_package_id=pkgs[1].id, specifier="^1.0.0"
        ),
        DependencyEdge(
            parent_version_id=vers[1].id, child_package_id=pkgs[2].id, specifier="^1.0.0"
        ),
        DependencyEdge(
            parent_version_id=vers[2].id, child_package_id=pkgs[0].id, specifier="^1.0.0"
        ),
    ]
    session.add_all(edges)
    await session.commit()

    # Run traversal from pkg_a (looking for everything that depends on it)
    # pkg_a is child of v_c. v_c is version of pkg_c.
    # pkg_c is child of v_b. v_b is version of pkg_b.
    # pkg_b is child of v_a. v_a is version of pkg_a.
    results = await get_blast_radius(session, pkgs[0].id, max_depth=5)

    # Should see pkg_c (depth 1), pkg_b (depth 2), pkg_a (depth 3), pkg_c (depth 4)...
    # DISTINCT in the query might collapse these, but let's check count.
    assert len(results) >= 2
    assert max(r["depth"] for r in results) <= 5


@pytest.mark.asyncio
async def test_cascading_edge_deletion(session: AsyncSession):
    """Assertion 2: Purges associated edges upon parent version removal."""
    p1 = Package(ecosystem="npm", name="parent")
    p2 = Package(ecosystem="npm", name="child")
    session.add_all([p1, p2])
    await session.commit()
    await session.refresh(p1)
    await session.refresh(p2)

    v1 = PackageVersion(package_id=p1.id, version_string="1.0.0")
    session.add(v1)
    await session.commit()
    await session.refresh(v1)

    edge = DependencyEdge(parent_version_id=v1.id, child_package_id=p2.id, specifier="*")
    session.add(edge)
    await session.commit()

    # Delete parent version
    await session.delete(v1)
    await session.commit()

    # Verify edge removal
    res = await session.execute(
        select(DependencyEdge).where(DependencyEdge.parent_version_id == v1.id)
    )
    assert len(res.scalars().all()) == 0


@pytest.mark.asyncio
async def test_forward_traversal_logic(session: AsyncSession):
    """Assertion 3: Correct identification of direct dependencies."""
    parent = Package(ecosystem="npm", name="react-dom")
    child = Package(ecosystem="npm", name="react")
    session.add_all([parent, child])
    await session.commit()
    await session.refresh(parent)
    await session.refresh(child)

    p_ver = PackageVersion(package_id=parent.id, version_string="18.2.0")
    session.add(p_ver)
    await session.commit()
    await session.refresh(p_ver)

    edge = DependencyEdge(
        parent_version_id=p_ver.id, child_package_id=child.id, specifier="^18.2.0"
    )
    session.add(edge)
    await session.commit()

    # Check relationship navigation
    res = await session.execute(
        select(DependencyEdge).where(DependencyEdge.parent_version_id == p_ver.id)
    )
    edge_found = res.scalars().one()
    assert edge_found.child_package_id == child.id
