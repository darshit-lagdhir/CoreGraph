# scripts/wipe_db.py
import asyncio
from sqlalchemy import text
from infra.database import db_manager

async def wipe():
    print("[WIPE] Dropping all logic in public schema...")
    async with db_manager.engine.begin() as conn:
        # 1. Drop Extensions & Tables Cascading
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    print("[SUCCESS] DB is blank as space.")

if __name__ == "__main__":
    asyncio.run(wipe())
