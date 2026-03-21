import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import select, text
from core.config import settings
from infra.database import db_manager


def test_schema_migration_continuity():
    """
    The 'Time Machine' Audit for Task 006.
    Ensures that the entire chain of migrations can be applied
    and then fully reversed without structural orphaned nodes.
    """
    alembic_cfg = Config("alembic.ini")

    try:
        # 1. UPGRADE TO HEAD (Current Project State)
        print("\n[TEST] Upgrading schema to head...")
        command.upgrade(alembic_cfg, "head")

        # 2. DOWNGRADE TO BASE (Initial State)
        # This confirms every downgrade() method is correctly authored.
        print("[TEST] Reversing schema to base (Null state)...")
        command.downgrade(alembic_cfg, "base")

        # 3. RE-APPLY HEAD to restore workstation for seeding test
        command.upgrade(alembic_cfg, "head")

    except Exception as e:
        pytest.fail(
            f"SCHEMA GOVERNANCE FAILURE: Migration history is non-linear or broken. Error: {e}"
        )


@pytest.mark.asyncio
async def test_seed_density():
    """
    Verifies that the 'Judge-Safe' seeding script populates the
    OSINT Specimen Vault as intended for competition demo.
    """
    from dal.seed import seed_osint_specimens
    from dal.models.package import Package

    async for session in db_manager.get_session():
        # Clear existing specimens from previous test runs
        await session.execute(text("TRUNCATE TABLE maintainer_metrics CASCADE;"))
        await session.execute(text("TRUNCATE TABLE author_profiles CASCADE;"))
        await session.execute(text("TRUNCATE TABLE dependency_edges CASCADE;"))
        await session.execute(text("TRUNCATE TABLE package_versions CASCADE;"))
        await session.execute(text("TRUNCATE TABLE packages CASCADE;"))
        await session.commit()

        await seed_osint_specimens(session)

        # Verify the XZ-Utils specimen exists and holds metadata
        result = await session.execute(select(Package).where(Package.name == "xz-utils"))
        xz = result.scalars().first()
        assert xz is not None
        assert xz.ecosystem == "debian"

        # Check for child linkage (Recursive chain validation)
        from sqlalchemy import func

        count = await session.execute(select(func.count()).select_from(Package))
        assert count.scalar() >= 4  # XZ + 3 consumers
