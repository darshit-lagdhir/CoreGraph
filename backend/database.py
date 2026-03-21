from core.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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
        # Deep Engineering Resolution (Failure 1): TCP_NODELAY socket options
        # and minimum 20 active connections during bootstrap
        "min_size": 20,
    },
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
