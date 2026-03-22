from typing import Dict, Any
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.graph import Package, PackageVersion
import logging


async def upsert_package_node(session: AsyncSession, package_data: Dict[str, Any]):
    """
    Idempotent insertion of a package node.
    The Mathematical Sink: f(f(E)) = f(E).
    Ensures that multiple ingestion signals do not create duplicate nodes.
    """
    # Using PostgreSQL specific 'ON CONFLICT' to ensure atomicity
    stmt = (
        insert(Package)
        .values(
            name=package_data["name"],
            ecosystem=package_data["ecosystem"],
            version_latest=package_data.get("version"),
        )
        .on_conflict_do_update(
            index_elements=["ecosystem", "name"],
            set_={"version_latest": package_data.get("version")},
        )
    )

    await session.execute(stmt)
    # The session should be committed by the caller (the Consumer Loop)
    logging.info(f"[PACKAGE_REPO] Idempotent Sync for {package_data['name']}")


async def upsert_version_node(session: AsyncSession, version_data: Dict[str, Any]):
    """Idempotent Versioning Sink."""
    # Find the package first
    from sqlalchemy import select

    package_res = await session.execute(
        select(Package.id).where(
            Package.name == version_data["name"], Package.ecosystem == version_data["ecosystem"]
        )
    )
    package_id = package_res.scalar()

    if not package_id:
        # Should we auto-create the package? Yes, for deep satellite discovery.
        await upsert_package_node(session, version_data)
        package_res = await session.execute(
            select(Package.id).where(
                Package.name == version_data["name"], Package.ecosystem == version_data["ecosystem"]
            )
        )
        package_id = package_res.scalar()

    # Calculate SemVer Components (Task 009: Mathematical Resolution)
    from dal.utils.semver import calculate_semver_components

    ma, mi, pa, pre, build, sk = calculate_semver_components(version_data["version"])

    # Now Upsert the Version with componentized fields for high-velocity range queries
    stmt = (
        insert(PackageVersion)
        .values(
            package_id=package_id,
            version_string=version_data["version"],
            version_major=ma,
            version_minor=mi,
            version_patch=pa,
            version_prerelease=pre,
            version_build=build,
            sort_key=sk,
            release_date=version_data.get("release_date"),
            metadata_extra=version_data.get("metadata", {}),
            is_stable=(pre is None or pre == "" or pre == "legacy"),
        )
        .on_conflict_do_update(
            index_elements=["package_id", "version_string"],
            set_={
                "version_major": ma,
                "version_minor": mi,
                "version_patch": pa,
                "sort_key": sk,
                "is_stable": (pre is None or pre == "" or pre == "legacy"),
            },
        )
    )

    await session.execute(stmt)

    # PULSE TRIGGER (Task 010: Node-Level Invalidation)
    # Surgical purging of the memory mirror to prevent OSINT staleness.
    from backend.infra.graph_cache import cache_manager

    await cache_manager.invalidate_node(str(package_id))

    logging.info(
        f"[VERSION_REPO] Idempotent Resolution Sync for {version_data['name']}@{version_data['version']}"
    )
