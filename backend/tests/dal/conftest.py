import pytest
import asyncio
from sqlalchemy import text
from dal.base import Base
from core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Import models to ensure they are registered with Base.metadata before create_all
from dal.models.graph import Package, PackageVersion, DependencyEdge
from dal.models.maintainer import AuthorProfile, MaintainerMetrics
from dal.models.temporal import GraphSnapshot, NodeDelta, EdgeDelta
from dal.models.criticality import CriticalityScore
from dal.models.partition import GraphCommunity, CommunityMembership
from dal.models.tiling import SummaryNode, VisualizationTile
from dal.models.integrity import MerkleNode, AuditBlock
from dal.models.telemetry import NodeTelemetry, HealthAnomaly
from dal.models.spatial import PackageSpatialIndex


@pytest.fixture
async def engine():
    engine = create_async_engine(settings.DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest.fixture(autouse=True)
async def setup_db(engine):
    """Purges the entire relational vault to ensure isolated OSINT audits."""
    async with engine.begin() as conn:
        # Nuclear purge of all known tables and views
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS dependency_edges CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS package_versions CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS packages CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS maintainer_metrics CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS author_profiles CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS criticality_scores CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS community_membership CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS graph_communities CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS summary_nodes CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS visualization_tiles CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS merkle_nodes CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS audit_blocks CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS node_telemetry CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS health_anomalies CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS package_spatial_index CASCADE;"))
        await conn.execute(
            text("DROP MATERIALIZED VIEW IF EXISTS mv_package_risk_summary CASCADE;")
        )
        await conn.execute(text("DROP TABLE IF EXISTS node_deltas CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS edge_deltas CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS graph_snapshots CASCADE;"))

        # Standardize extensions
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS cube;"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS earthdistance;"))

        # Re-initialize Ground Truth
        await conn.run_sync(Base.metadata.create_all)

        # Restore Analytical Engine (Materialized Views)
        await conn.execute(
            text(
                """
            CREATE MATERIALIZED VIEW mv_package_risk_summary AS
            SELECT
                p.id AS package_id,
                p.name,
                p.ecosystem,
                COALESCE(MAX(m.se_risk_score), 0.0) AS max_risk_score,
                COUNT(DISTINCT v.id) AS version_count
            FROM packages p
            LEFT JOIN package_versions v ON p.id = v.package_id
            LEFT JOIN maintainer_metrics m ON p.id = m.package_id
            GROUP BY p.id, p.name, p.ecosystem;
        """
            )
        )
        await conn.execute(
            text(
                "CREATE UNIQUE INDEX idx_mv_package_risk_pkg_id ON mv_package_risk_summary (package_id);"
            )
        )
    return


@pytest.fixture
def async_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def session(async_session_factory):
    async with async_session_factory() as session:
        yield session
