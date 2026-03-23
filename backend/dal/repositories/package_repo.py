import uuid
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.graph import Package, PackageVersion
from dal.utils.semver import calculate_semver_components
from infra.graph_cache import cache_manager


class PackageRepository:
    """
    CoreGraph Package Identity Module.
    Manages idempotent node resolution and SemVer-aware version chains.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_or_name(self, identifier: str) -> Optional[Package]:
        """Resolves a package node by UUID or Ecosystem/Name string."""
        try:
            # Check if identifier is a UUID
            node_id = uuid.UUID(identifier)
            stmt = select(Package).where(Package.id == node_id)
        except ValueError:
            # Format: ecosystem:name
            if ":" in identifier:
                eco, name = identifier.split(":", 1)
                stmt = select(Package).where(Package.ecosystem == eco, Package.name == name)
            else:
                stmt = select(Package).where(Package.name == identifier)

        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def upsert_package(self, package_data: Dict[str, Any]) -> uuid.UUID:
        """Idempotent sync for 3.88M node discovery."""
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
            .returning(Package.id)
        )
        res = await self.session.execute(stmt)
        return res.scalar()

    async def upsert_version(self, version_data: Dict[str, Any]):
        """Mathematical resolution of SemVer components and node-level invalidation."""
        package_id = await self.upsert_package(version_data)

        ma, mi, pa, pre, build, sk = calculate_semver_components(version_data["version"])

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
                is_stable=(pre is None or pre == "" or pre == "legacy"),
            )
            .on_conflict_do_update(
                index_elements=["package_id", "version_string"],
                set_={
                    "version_major": ma,
                    "version_minor": mi,
                    "version_patch": pa,
                    "sort_key": sk,
                },
            )
        )
        await self.session.execute(stmt)
        # Flush to memory mirror
        await cache_manager.invalidate_node(str(package_id))
        logging.info(f"[PACKAGE_REPO] Resolved {version_data['name']}@{version_data['version']}")
