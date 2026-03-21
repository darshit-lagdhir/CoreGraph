# alembic/env.py - High-Performance Asynchronous Migration Engine
import asyncio
import sys
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Ensure the backend directory is in the path for proper module discovery
sys.path.append(os.path.join(os.getcwd(), "backend"))

# COREGRAPH IMPORT PATHS - Ensuring Metadata Registry is populated
from dal.base import Base
from dal.models.package import Package
from dal.models.version import PackageVersion
from dal.models.dependency import DependencyEdge
from dal.models.maintainer import AuthorProfile, MaintainerMetrics
from infra.database import db_manager

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate functionality.
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates a SQL script for auditing before execution against the i9 vault.
    """
    url = db_manager.url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    """Execution bridge between the async engine and synchronous Alembic context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode for the i9 Beast or Supabase Cloud.
    Utilizes the hardware-aware DatabaseManager URL.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = db_manager.url

    # We use NullPool here to let DatabaseManager handle pooling elsewhere
    # and to ensure a fresh connection for the migration transaction.
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Use the established asyncio event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # In some deep-loop environments, we might need task creation
            loop.create_task(run_migrations_online())
        else:
            loop.run_until_complete(run_migrations_online())
    except RuntimeError:
        asyncio.run(run_migrations_online())
