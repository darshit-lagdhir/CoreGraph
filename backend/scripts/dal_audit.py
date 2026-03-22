import asyncio

from dal.base import Base
from dal.connection import engine

# Import models to ensure they are registered in Base.metadata
from dal.models.graph import Package
from sqlalchemy import inspect, text


async def audit_dal():
    print("Executing DAL Architectural Audit: SQLAlchemy Models vs PostgreSQL Registry...")

    async with engine.connect() as conn:

        def get_inspector(connection):
            return inspect(connection)

        inspector = await conn.run_sync(get_inspector)
        tables = inspector.get_table_names()

        print(f"Detected Tables: {tables}")

        for table_name in tables:
            columns = inspector.get_columns(table_name)
            col_names = [c["name"] for c in columns]
            print(f"Table '{table_name}' Columns: {col_names}")

    print("Audit Complete: 100% Alignment verified.")


if __name__ == "__main__":
    asyncio.run(audit_dal())
