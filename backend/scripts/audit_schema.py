import asyncio
import logging
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings
from models import Base


async def audit_schema_integrity():
    """Golden Master Verification: Comparing the physical relational vault against the SQLAlchemy models."""
    logging.info("Initiating Schema Integrity Audit...")
    
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.connect() as conn:
        def get_metadata(sync_conn):
            # 1. Inspecting the physical state of the PostgreSQL container
            inspector = inspect(sync_conn)
            return {
                "tables": set(inspector.get_table_names()),
                "indexes": {t: set(idx['name'] for idx in inspector.get_indexes(t)) for t in inspector.get_table_names()}
            }

        physical_state = await conn.run_sync(get_metadata)
        
        # 2. Extracting the expected state from the Python source code
        model_tables = set(Base.metadata.tables.keys())
        
        # 3. Category A Assertion: Zero-delta comparison
        missing_tables = model_tables - physical_state["tables"]
        extra_tables = physical_state["tables"] - model_tables - {"alembic_version"}
        
        if missing_tables:
            logging.error(f"STRUCTURAL_MISMATCH: Tables missing from DB: {missing_tables}")
        if extra_tables:
            logging.warning(f"UNTRACKED_ARTIFACDS: Tables found in DB not in models: {extra_tables}")

        if not missing_tables:
            logging.info("SCHEMA_AUDIT_PASSED: 100% topological alignment detected.")
        else:
            logging.error("SCHEMA_AUDIT_FAILED: Critical structural drift detected.")
            exit(1)

    await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(audit_schema_integrity())
