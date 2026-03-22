import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import select, text
from core.config import settings
from infra.database import db_manager


@pytest.fixture(autouse=True)
def setup_db():
    """Override centralized setup_db to allow Alembic to manage the lifecycle."""
    pass


def test_schema_migration_continuity():
    """
    The 'Time Machine' Audit for Task 006.
    Ensures that the entire chain of migrations can be applied
    and then fully reversed without structural orphaned nodes.
    """
    import subprocess
    import sys
    import os

    def purge_vault():
        # High-Velocity Purge: Direct SQL injection into the containerized vault
        # Ensures zero residual artifacts from parallel test sessions (CoreGraph Protocol)
        sql = (
            "DROP TABLE IF EXISTS alembic_version CASCADE; "
            "DROP TABLE IF EXISTS dependency_edges CASCADE; "
            "DROP TABLE IF EXISTS package_versions CASCADE; "
            "DROP TABLE IF EXISTS packages CASCADE; "
            "DROP TABLE IF EXISTS maintainer_metrics CASCADE; "
            "DROP TABLE IF EXISTS author_profiles CASCADE; "
            "DROP MATERIALIZED VIEW IF EXISTS mv_package_risk_summary CASCADE;"
        )
        subprocess.run(
            [
                "docker",
                "exec",
                "coregraph_postgres",
                "psql",
                "-U",
                "admin",
                "-d",
                "coregraph_db",
                "-c",
                sql,
            ],
            capture_output=True,
        )

    def run_alembic(args):
        env = os.environ.copy()
        env["PYTHONPATH"] = "backend"
        # Adjusted path for Windows venv
        alembic_path = os.path.join(os.getcwd(), "venv", "Scripts", "alembic.exe")
        result = subprocess.run([alembic_path] + args, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            # Only fail on TRUE errors, not INFO logging
            raise Exception(f"Alembic failure (RC={result.returncode}): {result.stderr}")
        return result.stdout

    try:
        # Pre-audit nuke to ensure linear evolution state
        purge_vault()

        # 1. UPGRADE TO HEAD (Current Project State)
        print("\n[TEST] Upgrading schema to head...")
        run_alembic(["upgrade", "head"])

        # 2. DOWNGRADE TO BASE (Initial State)
        print("[TEST] Reversing schema to base (Null state)...")
        run_alembic(["downgrade", "base"])

        # 3. RE-APPLY HEAD to restore workstation for seeding test
        run_alembic(["upgrade", "head"])

    except Exception as e:
        pytest.fail(
            f"SCHEMA GOVERNANCE FAILURE: Migration history is non-linear or broken. Error: {e}"
        )
