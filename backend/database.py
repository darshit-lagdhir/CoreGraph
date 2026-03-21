from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=32,
    max_overflow=16,
    pool_timeout=30.0,
    pool_recycle=1200,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
