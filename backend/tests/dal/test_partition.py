import pytest
import uuid
from sqlalchemy import select
from dal.models.graph import Package, PackageVersion, DependencyEdge
from dal.models.partition import GraphCommunity, CommunityMembership
from dal.queries.partition import compute_louvain_communities
from dal.repositories.sda_repo import SegmentedDataAccess


@pytest.mark.asyncio
async def test_community_cohesion_and_modularity(session):
    """
    Verifies that the topological segmentation produces significant modularity (Q)
    and clusters related entities (e.g., React-prefixed silos).
    """
    # 1. Setup Silo (Foundation: React, Consumers: react-dom, react-native)
    react = Package(name="react", ecosystem="npm")
    session.add(react)
    await session.commit()
    await session.refresh(react)

    v_react = PackageVersion(package_id=react.id, version_string="18.2.0")
    session.add(v_react)
    await session.commit()
    await session.refresh(v_react)

    # Consumers
    for name in ["react-dom", "react-native", "react-redux"]:
        leaf = Package(name=name, ecosystem="npm")
        session.add(leaf)
        await session.commit()
        await session.refresh(leaf)

        v_leaf = PackageVersion(package_id=leaf.id, version_string="1.0.0")
        session.add(v_leaf)
        await session.commit()
        await session.refresh(v_leaf)

        edge = DependencyEdge(
            parent_version_id=v_leaf.id, child_package_id=react.id, specifier="^18.2.0"
        )
        session.add(edge)

    await session.commit()

    # Silo 2: The Angular Authority
    angular = Package(name="angular", ecosystem="npm")
    session.add(angular)
    await session.commit()
    await session.refresh(angular)

    v_ang = PackageVersion(package_id=angular.id, version_string="15.0.0")
    session.add(v_ang)
    await session.commit()
    await session.refresh(v_ang)

    for name in ["rxjs", "zone.js"]:
        leaf = Package(name=name, ecosystem="npm")
        session.add(leaf)
        await session.commit()
        await session.refresh(leaf)

        v_leaf = PackageVersion(package_id=leaf.id, version_string="1.0.0")
        session.add(v_leaf)
        await session.commit()
        await session.refresh(v_leaf)

        edge = DependencyEdge(
            parent_version_id=v_leaf.id, child_package_id=angular.id, specifier="^15.0.0"
        )
        session.add(edge)

    await session.commit()

    # 2. Trigger Louvain Kernel
    q_final = await compute_louvain_communities(session)

    # Validation: Modularity is a scalar [0..1]
    assert q_final > 0.0

    # 3. Check for Cohesion (All react-related in the same community)
    result = await session.execute(
        select(CommunityMembership.community_id).join(Package).where(Package.name == "react")
    )
    react_comm_id = result.scalar()
    assert react_comm_id is not None

    leaf_res = await session.execute(
        select(CommunityMembership.community_id).join(Package).where(Package.name == "react-dom")
    )
    dom_comm_id = leaf_res.scalar()

    # In a small tight-knit sample, they should share a community (Topological Cohesion)
    assert react_comm_id == dom_comm_id


@pytest.mark.asyncio
async def test_sda_isolation_protocol(session):
    """
    Asserts that the Segmented Data Access session enforces hard-boundary
    isolation for sub-graph analysis.
    """
    # 1. Setup isolated silos
    comm_a = GraphCommunity(id=uuid.uuid4())
    comm_b = GraphCommunity(id=uuid.uuid4())
    pkg_a = Package(name="package-a", ecosystem="npm")
    pkg_b = Package(name="package-b", ecosystem="npm")
    session.add_all([comm_a, comm_b, pkg_a, pkg_b])
    await session.commit()
    await session.refresh(pkg_a)
    await session.refresh(pkg_b)

    # Assignments
    mem_a = CommunityMembership(package_id=pkg_a.id, community_id=comm_a.id)
    mem_b = CommunityMembership(package_id=pkg_b.id, community_id=comm_b.id)
    session.add_all([mem_a, mem_b])
    await session.commit()

    # 2. SDA Access: Session A
    sda = SegmentedDataAccess(community_id=comm_a.id)

    # 3. Query Execution: Attempt to find package-b while in Session A
    query = sda.apply_segmentation(select(Package).where(Package.name == "package-b"))
    res = await session.execute(query)

    # Assertion: Segmented access must return zero results for external nodes.
    assert len(res.all()) == 0

    # Success: Attempt to find package-a
    query_a = sda.apply_segmentation(select(Package).where(Package.name == "package-a"))
    res_a = await session.execute(query_a)
    assert len(res_a.all()) == 1
