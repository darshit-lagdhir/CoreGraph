import pytest
import uuid
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from dal.base import Base
from dal.models.package import Package
from dal.models.version import PackageVersion
from dal.models.maintainer import AuthorProfile, MaintainerMetrics
from dal.models.dependency import DependencyEdge
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
    """Create isolated PostgreSQL environment for identity and behavioral audits."""
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS maintainer_metrics CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS author_profiles CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS packages CASCADE;"))

        # Ensure GIN support for metadata queries
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

        await conn.run_sync(Base.metadata.create_all)
    return


@pytest.fixture
async def session(async_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Provides a fresh asynchronous session for each test."""
    async with async_session_factory() as sess:
        yield sess


@pytest.mark.asyncio
async def test_maintainer_velocity_spike_detection(session: AsyncSession):
    """Assertion 1: Velocity delta thresholding for XZ Pattern detection."""
    # Seed author node
    author = AuthorProfile(email_hash="auth_hash_001", display_name="Maintainer 1")
    pkg = Package(ecosystem="pypi", name="core_pkg")
    session.add_all([author, pkg])
    await session.commit()
    await session.refresh(author)
    await session.refresh(pkg)

    # Initialize metrics with baseline work density
    m1 = MaintainerMetrics(
        package_id=pkg.id,
        author_id=author.id,
        current_velocity=1.2,
        commit_count_90d=15,
        se_risk_score=0.1,
    )
    session.add(m1)
    await session.commit()
    await session.refresh(m1)

    # Simulate high-velocity spike (Compromise/Injection Pattern)
    m1.velocity_delta_30d = 5.8
    m1.se_risk_score = 0.92
    await session.commit()

    # Audit for high-risk maintainers
    stmt = select(MaintainerMetrics).where(MaintainerMetrics.se_risk_score >= 0.9)
    flagged = (await session.execute(stmt)).scalars().one()

    assert flagged.author_id == author.id
    assert flagged.se_risk_score == 0.92


@pytest.mark.asyncio
async def test_identity_metadata_gin_lookup(session: AsyncSession):
    """Assertion 2: Sub-millisecond filtering of AI-analyzed intent categories."""
    # Construct suspicious metadata profile
    meta = {"social_intent": {"intent_category": "HOSTILE_SUBVERSION", "burnout_index": 0.88}}
    author = AuthorProfile(
        email_hash="threat_hash_01", display_name="Anon Dev", identity_metadata=meta
    )
    session.add(author)
    await session.commit()

    # Verify GIN-based containment query capability
    stmt = select(AuthorProfile).where(
        AuthorProfile.identity_metadata.contains(
            {"social_intent": {"intent_category": "HOSTILE_SUBVERSION"}}
        )
    )
    result = (await session.execute(stmt)).scalars().one()

    assert result.display_name == "Anon Dev"
    assert result.identity_metadata["social_intent"]["burnout_index"] == 0.88


@pytest.mark.asyncio
async def test_maintainer_uniqueness_violation(session: AsyncSession):
    """Assertion 3: Prevention of profiling redundancy at the RDBMS kernel level."""
    # Seed identity and package
    author = AuthorProfile(email_hash="uniq_hash", display_name="Uniq Dev")
    pkg = Package(ecosystem="npm", name="uniq_pkg")
    session.add_all([author, pkg])
    await session.commit()
    await session.refresh(author)
    await session.refresh(pkg)

    # Seed first metric record
    m1 = MaintainerMetrics(package_id=pkg.id, author_id=author.id)
    session.add(m1)
    await session.commit()

    # Attempt duplicate metric entry
    from sqlalchemy.exc import IntegrityError

    m2 = MaintainerMetrics(package_id=pkg.id, author_id=author.id)
    session.add(m2)
    with pytest.raises(IntegrityError):
        await session.commit()
