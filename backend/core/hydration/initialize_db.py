import asyncio
import os
import logging
import asyncpg
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def initialize_supabase_schema():
    """
    SECTOR KAPPA: Supabase Schema Ignition.
    Executes the initial_schema.sql to prepare the vault for hydration.
    """
    db_url = os.getenv("CLOUD_DATABASE_URL")
    if not db_url:
        logger.error("CLOUD_DATABASE_URL not found in .env")
        return

    # Normalize URL for asyncpg (remove +asyncpg if present)
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")

    logger.info(f"Connecting to Supabase Vault at {db_url.split('@')[-1]}...")

    try:
        conn = await asyncpg.connect(db_url)

        # Read the SQL schema
        schema_path = os.path.join(os.path.dirname(__file__), "initial_schema.sql")
        with open(schema_path, "r") as f:
            sql = f.read()

        logger.info("Executing Schema Ignition...")
        await conn.execute(sql)

        logger.info("Supabase Vault Schema Initialized Successfully (Sector Kappa).")
        await conn.close()
    except Exception as e:
        logger.error(f"Schema Ignition failed: {e}")


if __name__ == "__main__":
    asyncio.run(initialize_supabase_schema())
