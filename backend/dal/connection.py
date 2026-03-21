from typing import AsyncGenerator

from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

# Engineering of the Connection Pool (Module 1 established, Module 2 DAL maintains)
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=32,
    max_overflow=16,
    pool_timeout=30.0,
    pool_recycle=1200,
    echo=False,
    connect_args={
        "server_settings": {
            "tcp_keepalives_idle": "60",
            "tcp_user_timeout": "1000",
        },
        # TCR_NODELAY and Minimum size 20 (Failure 3 Resolution in Module 1)
        "min_size": 20,
    },
)

# Centralized Async Session Maker
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an asynchronous database session."""
    async with async_session() as session:
        yield session
