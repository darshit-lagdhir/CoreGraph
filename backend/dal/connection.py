from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from infra.database import db_manager

# Re-exposing the Singleton to maintain backward compatibility for existing code.
engine = db_manager.engine
async_session = db_manager.session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining an asynchronous database session via the infra singleton."""
    async for session in db_manager.get_session():
        yield session
