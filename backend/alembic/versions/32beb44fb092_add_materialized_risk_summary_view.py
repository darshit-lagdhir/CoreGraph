"""add materialized risk summary view

Revision ID: 32beb44fb092
Revises: aa2b8214f405
Create Date: 2026-03-22 13:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "32beb44fb092"
down_revision = "aa2b8214f405"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. CREATE MATERIALIZED VIEW for HUD Risk Mapping (Task 006)
    # Optimized for O(1) latency across the 3.88M node ecosystem
    op.execute("""
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
    """)

    # 2. Add Unique Index for CONCURRENT refresh (CoreGraph Protocol)
    op.execute(
        "CREATE UNIQUE INDEX idx_mv_package_risk_pkg_id ON mv_package_risk_summary (package_id);"
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_package_risk_summary CASCADE;")
