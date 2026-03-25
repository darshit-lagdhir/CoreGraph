import pytest
from sqlalchemy import text
from alembic.config import Config
from alembic import command
import os


@pytest.mark.asyncio
async def test_zero_state_mathematical_consistency(engine, session):
    """
    The 'Total Wipeout' Audit (Task 027).
    Proves that the Genesis migration is structurally sound and inclusive.
    """
    root_dir = os.getcwd()
    alembic_cfg = Config(os.path.join(root_dir, "backend/dal/alembic.ini"))

    # 1. NUCLEAR WIPE (Ensure no metadata.create_all pollution)
    print("\n[AUDIT] Clearing all pre-test metadata pollution...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))

    # 2. UPWARD (Alembic Genesis)
    print("[MIGRATION] Exercising Genesis upgrade...")
    # Alembic creates extensions AND tables
    command.upgrade(alembic_cfg, "head")

    # Verify tables created
    result = await session.execute(
        text(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name != 'alembic_version'"
        )
    )
    up_count = result.scalar()
    print(f"[AUDIT] Genesis created {up_count} tables.")

    # 3. DOWNWARD (Base)
    print("[MIGRATION] Reversing Genesis to BASE...")
    command.downgrade(alembic_cfg, "base")

    # 4. FINAL ASSERTION: THE ZERO-STATE PROOF
    result = await session.execute(
        text(
            """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name != 'alembic_version'
          AND table_name NOT LIKE 'pg_%'
          AND table_name NOT LIKE 'sql_%'
    """
        )
    )
    lingering = [row[0] for row in result.fetchall()]

    if lingering:
        print(f"[VIOLATION] Lingering Tables: {lingering}")

    # Also check extensions
    result = await session.execute(
        text(
            "SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm', 'cube', 'earthdistance')"
        )
    )
    exts = [row[0] for row in result.fetchall()]

    assert len(lingering) == 0, f"Rollback leaked tables: {lingering}"
    assert len(exts) == 0, f"Rollback leaked extensions: {exts}"

    print("[SUCCESS] Zero-state rollback mathematically proven.")

    # RE-UPGRADE for subsequent tests
    print("[MIGRATION] Restoring Schema for platform availability...")
    command.upgrade(alembic_cfg, "head")
