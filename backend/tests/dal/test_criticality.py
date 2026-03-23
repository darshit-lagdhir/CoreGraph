import pytest
import uuid
import sqlalchemy as sa
from sqlalchemy import select
from dal.models.graph import Package, PackageVersion, DependencyEdge
from dal.models.maintainer import MaintainerMetrics, AuthorProfile
from dal.models.criticality import CriticalityScore
from dal.queries.criticality import compute_global_criticality, get_top_critical_nodes


@pytest.mark.asyncio
async def test_criticality_ranking_accuracy(session):
    """
    Verifies that the $C_{idx}$ engine correctly ranks
    known foundations (Authorities) higher than leaf nodes.
    """
    # 1. Setup a mini graph (Authority: Lodash, Consumers: 5 leaf nodes)
    # This creates a topological centrality for 'lodash'
    lodash = Package(name="lodash", ecosystem="npm")
    session.add(lodash)
    await session.commit()
    await session.refresh(lodash)

    # Lodash version
    v_lodash = PackageVersion(package_id=lodash.id, version_string="4.17.21")
    session.add(v_lodash)
    await session.commit()
    await session.refresh(v_lodash)

    # 5 Consumers (Leaf nodes)
    for i in range(5):
        leaf = Package(name=f"leaf-{i}", ecosystem="npm")
        session.add(leaf)
        await session.commit()
        await session.refresh(leaf)

        v_leaf = PackageVersion(package_id=leaf.id, version_string="1.0.0")
        session.add(v_leaf)
        await session.commit()
        await session.refresh(v_leaf)

        # Edge: leaf depends on lodash
        edge = DependencyEdge(
            parent_version_id=v_leaf.id, child_package_id=lodash.id, specifier="^4.17.21"
        )
        session.add(edge)

    await session.commit()

    # 2. Add an obscure package (No dependents)
    obscure = Package(name="some-obscure-pkg", ecosystem="npm")
    session.add(obscure)
    await session.commit()
    await session.refresh(obscure)

    # 3. Trigger the Power Iteration Kernel
    await compute_global_criticality(session)

    # 4. Fetch the scores
    res_lodash = await session.execute(
        select(CriticalityScore).where(CriticalityScore.package_id == lodash.id)
    )
    score_lodash = res_lodash.scalars().first()

    res_obscure = await session.execute(
        select(CriticalityScore).where(CriticalityScore.package_id == obscure.id)
    )
    score_obscure = res_obscure.scalars().first()

    # 5. Validation: Foundational packages MUST have higher scores
    # C_idx includes topological (Eigenvector) + reach (Blast Radius) + velocity (Social)
    assert score_lodash is not None
    assert score_obscure is not None
    assert score_lodash.c_idx > score_obscure.c_idx
    assert score_lodash.authority_score > 0.0


@pytest.mark.asyncio
async def test_velocity_impact_on_criticality(session):
    """
    Ensures that a high velocity spike correctly boosts the $C_{idx}$ of a package.
    $C_{idx} = 0.5 * Psi + 0.2 * Vc + 0.3 * ln(1+Br)$
    """
    # 1. Setup author and package
    author = AuthorProfile(email_hash="auth-1")
    pkg = Package(name="velocity-pkg", ecosystem="pypi")
    session.add_all([author, pkg])
    await session.commit()
    await session.refresh(pkg)
    await session.refresh(author)

    # Stable velocity at start
    metrics = MaintainerMetrics(author_id=author.id, package_id=pkg.id, current_velocity=1.0)
    session.add(metrics)
    await session.commit()

    # Initial Re-compute
    await compute_global_criticality(session)
    res_v1 = await session.execute(
        select(CriticalityScore).where(CriticalityScore.package_id == pkg.id)
    )
    c1 = res_v1.scalars().first().c_idx

    # 2. Inject 50x velocity spike
    metrics.current_velocity = 50.0
    session.add(metrics)
    await session.commit()

    # 3. Re-compute
    await compute_global_criticality(session)
    res_v2 = await session.execute(
        select(CriticalityScore).where(CriticalityScore.package_id == pkg.id)
    )
    c2 = res_v2.scalars().first().c_idx

    # Assertion: c_idx should increase
    assert c2 > c1
