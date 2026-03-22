import pytest
import uuid
import sqlalchemy as sa
from dal.base import Base
from dal.models.graph import Package, PackageVersion, DependencyEdge
from dal.models.maintainer import AuthorProfile, MaintainerMetrics
from dal.utils.semver import resolve_best_candidate, calculate_semver_components
from infra.database import db_manager


@pytest.mark.parametrize(
    "version_str, expected",
    [
        ("1.2.3", (1, 2, 3, None, None, "00001.00002.00003")),
        ("v2.0.0-beta.1", (2, 0, 0, "beta.1", None, "00002.00000.00000")),
        ("1.0.0+build.42", (1, 0, 0, None, "build.42", "00001.00000.00000")),
        ("2023.01.01", (2023, 1, 1, None, None, "02023.00001.00001")),
    ],
)
def test_semver_component_parsing(version_str, expected):
    """Verifies that raw version strings are correctly decomposed for indexing."""
    res = calculate_semver_components(version_str)
    assert res == expected


@pytest.mark.asyncio
async def test_high_velocity_range_resolution(session):
    """
    Simulation of HUD range resolution across candidate versions.
    Verifies that 'resolve_best_candidate' uses componentized indexing.
    """
    pkg_name = f"semver-pkg-{uuid.uuid4().hex[:8]}"

    # 1. Create Package via Raw SQL to avoid Mapper issues (Temporal Vault Isolation)
    pkg_id = uuid.uuid4()
    await session.execute(
        sa.text("INSERT INTO packages (id, name, ecosystem) VALUES (:id, :name, 'npm')"),
        {"id": pkg_id, "name": pkg_name},
    )
    await session.commit()

    versions = [
        ("1.2.2", 1, 2, 2, "00001.00002.00002", True),
        ("1.2.3", 1, 2, 3, "00001.00002.00003", True),
        ("1.3.0", 1, 3, 0, "00001.00003.00000", True),
        ("2.0.0-beta", 2, 0, 0, "00002.00000.00000", False),  # Unstable
    ]

    for vstr, ma, mi, pa, sk, stable in versions:
        await session.execute(
            sa.text(
                """INSERT INTO package_versions
                 (id, package_id, version_string, version_major, version_minor, version_patch, sort_key, is_stable)
                 VALUES (gen_random_uuid(), :pid, :vs, :ma, :mi, :pa, :sk, :st)"""
            ),
            {"pid": pkg_id, "vs": vstr, "ma": ma, "mi": mi, "pa": pa, "sk": sk, "st": stable},
        )
    await session.commit()

    # Test 1: Caret Range ^1.2.0 -> Should resolve to 1.3.0
    best = await resolve_best_candidate(session, str(pkg_id), "^1.2.0")
    assert best is not None
    assert best.version_string == "1.3.0"

    # Test 2: Tilde Range ~1.2.0 -> Should resolve to 1.2.3 (highest in 1.2.x)
    best = await resolve_best_candidate(session, str(pkg_id), "~1.2.0")
    assert best is not None
    assert best.version_string == "1.2.3"

    # Test 3: Stability Guard -> ^2.0.0 should return None (beta is unstable)
    best = await resolve_best_candidate(session, str(pkg_id), "^2.0.0")
    assert best is None
