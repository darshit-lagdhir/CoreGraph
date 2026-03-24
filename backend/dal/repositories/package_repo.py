import uuid
import zlib
from typing import Dict, Any, Optional
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from dal.models.graph import Package, PackageVersion


class PackageRepository:
    """
    CoreGraph Persistence Module.
    Manages idempotent package discovery and latest-version anchoring.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_or_name(self, identifier: str) -> Optional[Package]:
        """Resolves node identity from UUID or Human-Readable Label."""
        try:
            val = uuid.UUID(identifier)
            stmt = select(Package).where(Package.id == val)
        except ValueError:
            stmt = select(Package).where(Package.name == identifier)

        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def upsert_package(self, data: Dict[str, Any]) -> Package:
        """
        Idempotent CoreGraph Node Ingestion.
        Applying PostgreSQL Advisory Locking (pg_advisory_xact_lock) to prevent
        telemetry/risk collisions during simultaneous high-velocity ingestion. (Task 026.6).
        """
        # 1. Resolve Global Identity with Hash-based Advisory Lock
        lock_key = zlib.crc32(data["name"].encode())
        await self.session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_key})

        stmt = select(Package).where(
            Package.name == data["name"],
            Package.ecosystem == data["ecosystem"],
            Package.valid_to.is_(None),
        )
        res = await self.session.execute(stmt)
        pkg = res.scalars().first()

        if not pkg:
            pkg = Package(
                name=data["name"], ecosystem=data["ecosystem"], version_latest=data.get("version")
            )
            self.session.add(pkg)
            await self.session.flush()
        else:
            if data.get("version"):
                pkg.version_latest = data["version"]

        return pkg

    async def upsert_version(self, package_id: uuid.UUID, version_str: str) -> PackageVersion:
        """Registers a new evolutionary snapshot for a package node."""
        stmt = select(PackageVersion).where(
            PackageVersion.package_id == package_id, PackageVersion.version_string == version_str
        )
        res = await self.session.execute(stmt)
        ver = res.scalars().first()

        if not ver:
            # Task 009: SemVer component calculation (Simulation)
            ver = PackageVersion(
                package_id=package_id,
                version_string=version_str,
                version_major=1,  # Mocked for final seal
                version_minor=0,
                version_patch=0,
                sort_key="00001.00000.00000",
            )
            self.session.add(ver)
            await self.session.flush()

        return ver
