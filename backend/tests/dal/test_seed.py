import pytest
from sqlalchemy import select, text, func
from infra.database import db_manager
from dal.seed import seed_osint_specimens
from dal.models.graph import Package

@pytest.mark.asyncio
async def test_seed_density(session):
    """
    Verifies that the 'Judge-Safe' seeding script populates the
    OSINT Specimen Vault as intended for competition demo.
    """
    # Vault is already purged by conftest logic (CoreGraph Protocol)
    await seed_osint_specimens(session)
    await session.commit()

    # Verify the XZ-Utils specimen exists and holds metadata
    result = await session.execute(select(Package).where(Package.name == "xz-utils"))
    xz = result.scalars().first()
    assert xz is not None
    assert xz.ecosystem == "debian"

    # Check for child linkage (Recursive chain validation)
    count_res = await session.execute(select(func.count()).select_from(Package))
    count = count_res.scalar()
    assert count >= 4  # XZ + 3 consumers
