import os
import asyncio
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import text
from core.config import settings

# Load hardware mode from our settings/env nervous system
COREGRAPH_MODE = os.getenv("COREGRAPH_MODE", "LITE")


class DatabaseManager:
    """
    The High-Speed Highway Singleton for CoreGraph.
    Manages the lifecycle of asynchronous connections to the PostgreSQL vault.

    Architectural Mandate:
    - BEAST Mode: Maximize throughput for the i9-13980hx.
    - LITE Mode: Cap resources for Supabase/Judge hardware.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        if COREGRAPH_MODE == "BEAST":
            self.pool_size = 25
            self.max_overflow = 50
            self.pool_timeout = 30
            self.url = settings.DATABASE_URL
            self.echo = False
        else:
            self.pool_size = 10
            self.max_overflow = 0
            self.pool_timeout = 60
            self.url = os.getenv("CLOUD_DATABASE_URL", settings.DATABASE_URL)
            self.echo = True

        self.engine = create_async_engine(
            self.url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=1800,
            pool_pre_ping=True,
            connect_args={"prepared_statement_cache_size": 500},
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )
        self._initialized = True
        logging.info(f"Database Highway initialized in {COREGRAPH_MODE} mode.")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Dependency Injection provider for the FastAPI HUD.
        Ensures every request gets a dedicated, isolated session.
        """
        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                logging.error(f"Database Transaction Error: {e}")
                await session.rollback()
                raise
            # Session factory's context manager handles closure automatically.

    async def verify_connection(self):
        """Hardware startup check."""
        async with self.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logging.info("CoreGraph persistence link verified.")


# Global singleton accessor
db_manager = DatabaseManager()
