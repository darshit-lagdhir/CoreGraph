import asyncio
import os
import asyncpg
import logging
from infra.events import cache_event_bus

# Module 2, Task 008: PostgreSQL PostgreSQL LISTEN/NOTIFY Engine
# Allows the PostgreSQL Vault to 'talk back' to the 144Hz HUD.


async def listen_for_db_changes():
    """
    Subscribes to internal PostgreSQL signals.
    Allows the database to trigger HUD updates without polling the highways.
    """
    # Using the hardware-aware URL from settings
    db_url = os.getenv("DATABASE_URL", "postgresql://admin:password@localhost:5433/coregraph_db")
    # asyncpg binary connection for sub-millisecond signal transfer
    conn = await asyncpg.connect(db_url)

    def callback(connection, pid, channel, payload):
        logging.info(f"[DB_SIGNAL] Received {channel}: {payload}")
        # Forward the internal DB event into the Global Event Bus
        # This allows the HUD (listening to Redis) to Hot-Reload Risk Views.
        asyncio.create_task(
            cache_event_bus.publish_event(
                "HUD_REFRESH_REQUESTED", {"source": channel, "pid": pid, "payload": payload}
            )
        )

    # Listen for Materialized View Refreshes (Task 007 Completion)
    await conn.add_listener("risk_view_refreshed", callback)
    logging.info("[DB_NOTIFY] CoreGraph persistence listener active.")

    # Keeping the listener loop alive for as long as the i9 workstation is 'armed'
    try:
        while True:
            await asyncio.sleep(60)  # Heartbeat
    finally:
        await conn.close()
