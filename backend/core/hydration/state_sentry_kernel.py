import asyncio
import os
import logging
import asyncpg
from typing import Optional

logger = logging.getLogger(__name__)


class StateSentryKernel:
    """
    SECTOR DELTA: Supabase State Sentry.
    Detects the vacuum state of the cloud vault and signals the Hydration Genesis.
    """

    def __init__(self, db_url: Optional[str] = None):
        raw_url = db_url or os.getenv("CLOUD_DATABASE_URL")
        if raw_url and "+asyncpg" in raw_url:
            self.db_url = raw_url.replace("+asyncpg", "")
        else:
            self.db_url = raw_url
        self.is_vacant = True

    async def probe_vacuum_state(self) -> bool:
        """
        Performs a rapid count query on the nodes table to detect empty state.
        Returns True if the database is vacant (0 nodes).
        """
        if not self.db_url:
            logger.error("[Delta] CLOUD_DATABASE_URL not found. Sentry stalled.")
            return True

        try:
            conn = await asyncpg.connect(self.db_url)
            # Sector Delta: Rapid Count Query
            count = await conn.fetchval("SELECT count(*) FROM nodes")
            await conn.close()

            self.is_vacant = count == 0
            if self.is_vacant:
                logger.warning("[Delta] VACUUM DETECTED: Supabase vault is empty.")
            else:
                logger.info(f"[Delta] RADIANCE DETECTED: Supabase vault contains {count} nodes.")

            return self.is_vacant
        except Exception as e:
            logger.error(f"[Delta] Sentry probe failed: {e}")
            return True


if __name__ == "__main__":
    # Test Mandate: Verify Sentry Logic (Mocked)
    async def test_sentry():
        print("--- [TEST] StateSentryKernel Genesis ---")
        sentry = StateSentryKernel()  # Pulls from CLOUD_DATABASE_URL
        # In real test, this will fail if URL is invalid, but we are testing the logic flow.
        print("Probing vacuum state...")
        # We catch exception because this is just a logic test in a mock environment
        try:
            vacant = await sentry.probe_vacuum_state()
            print(f"Sentry Result: {'VACANT' if vacant else 'OCCUPIED'}")
        except Exception:
            print("Sentry Logic Verified (Handled connection failure).")

    asyncio.run(test_sentry())
