import asyncio
import time
import uuid
from typing import AsyncGenerator

import pytest
from core.config import settings
from dal.base import Base
from dal.models.package import Package
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
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
        # Deep Engineering Resolution: Handle dependent objects from Module 1
        await conn.execute(text("DROP TABLE IF EXISTS dependencies CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS maintainer_health CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS financial_health CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS packages CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))

        # Enable pg_trgm for GIN Index
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

        # Create new foundational schema
        await conn.run_sync(Base.metadata.create_all)
    return


@pytest.fixture
async def session(
    async_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Provides a fresh asynchronous session for each test."""
    async with async_session_factory() as sess:
        yield sess


@pytest.mark.asyncio
async def test_uuid_generation_persistence(session: AsyncSession):
    """Assertion 1: UUIDv4 assigned and mapped correctly from DB kernel."""
    new_pkg = Package(ecosystem="pypi", name="requests", version_latest="2.31.0")
    session.add(new_pkg)
    await session.commit()
    await session.refresh(new_pkg)

    assert isinstance(new_pkg.id, uuid.UUID)
    assert new_pkg.ecosystem == "pypi"
    assert new_pkg.name == "requests"


@pytest.mark.asyncio
async def test_composite_uniqueness_violation(session: AsyncSession):
    """Assertion 2: (Ecosystem, Name) violation raises IntegrityError."""
    p1 = Package(ecosystem="pypi", name="sqlalchemy")
    session.add(p1)
    await session.commit()

    p2 = Package(ecosystem="pypi", name="sqlalchemy")
    session.add(p2)
    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.asyncio
async def test_ecosystem_differentiation(session: AsyncSession):
    """Assertion 3: Coexistence of same Name across different Ecosystems."""
    p1 = Package(ecosystem="pypi", name="requests_multi")
    p2 = Package(ecosystem="npm", name="requests_multi")
    session.add_all([p1, p2])
    await session.commit()

    res = await session.execute(select(Package).where(Package.name == "requests_multi"))
    pkgs = res.scalars().all()
    assert len(pkgs) == 2


@pytest.mark.asyncio
async def test_string_constraint_enforcement(session: AsyncSession):
    """Assertion 4: Rejection of name exceeding 255-character memory boundary."""
    long_name = "x" * 256
    p1 = Package(ecosystem="pypi", name=long_name)
    session.add(p1)
    with pytest.raises(Exception):
        await session.commit()


@pytest.mark.asyncio
async def test_asynchronous_retrieval_latency(session: AsyncSession):
    """Assertion 5: Bulk ingestion and retrieval benchmarking on NVMe."""
    pkgs = [Package(ecosystem="pypi", name=f"pkg_{i}") for i in range(100)]
    session.add_all(pkgs)
    await session.commit()

    start_time = time.perf_counter()
    stmt = select(Package)
    res = await session.execute(stmt)
    results = res.scalars().all()
    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000
    assert len(results) >= 100
    assert latency_ms < 50.0


@pytest.mark.asyncio
async def test_transactional_rollback(session: AsyncSession):
    """Assertion 6: proof that async with transaction manager is functioning."""
    try:
        async with session.begin():
            for i in range(50):
                session.add(Package(ecosystem="pypi", name=f"trans_{i}"))
            # Injected failure: violation of uniqueness
            session.add(Package(ecosystem="pypi", name="trans_0"))
            await session.flush()
    except IntegrityError:
        await session.rollback()

    # Verify rollback
    res = await session.execute(select(Package).where(Package.name.like("trans_%")))
    assert len(res.scalars().all()) == 0


@pytest.mark.asyncio
async def test_case_insensitive_collision_resolution(session: AsyncSession):
    """Failure 1 Resolution verification: Requests vs requests."""
    p1 = Package(ecosystem="pypi", name="Requests")
    session.add(p1)
    await session.commit()

    p2 = Package(ecosystem="pypi", name="requests")
    session.add(p2)
    with pytest.raises(IntegrityError):
        await session.commit()
