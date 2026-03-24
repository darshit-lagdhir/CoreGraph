# scripts/generate_genesis.py
import sys
import os
from sqlalchemy import create_mock_engine

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Import all models to populate Base.metadata
from dal.base import Base
from dal.models import graph, maintainer, alerting, annotation, backup, criticality, export, integrity, partition, risk_scoring, spatial, telemetry, temporal, tiling

def dump_sql(sql, *multiparams, **params):
    print(sql.compile(dialect=engine.dialect))

engine = create_mock_engine("postgresql+asyncpg://", dump_sql)

# This will print the SQL, but I want Alembic commands.
# I'll just look at metadata.tables and print create_table lines.
for table in Base.metadata.sorted_tables:
    print(f"op.create_table('{table.name}', ...)")
