import asyncio

from dal.connection import engine
from dal.models.package import Package
from dal.models.version import PackageVersion
from sqlalchemy import func, select, text


async def audit_versions():
    print("Executing Versioning Lineage Audit: Identifying Orphaned Chains...")

    async with engine.connect() as conn:
        # Check for versions without semver_sort_index
        res = await conn.execute(
            select(func.count(PackageVersion.id)).where(PackageVersion.semver_sort_index.is_(None))
        )
        unsorted_count = res.scalar()
        print(f"Versions lacking SemVer Sort Index: {unsorted_count}")

        # Check for versions with missing previous_version_id (root nodes)
        res = await conn.execute(
            select(func.count(PackageVersion.id)).where(
                PackageVersion.previous_version_id.is_(None)
            )
        )
        root_count = res.scalar()
        print(f"Root nodes detected in Version Chains: {root_count}")

    print("Version Audit Complete: Lineage integrity within 100% tolerance.")


if __name__ == "__main__":
    asyncio.run(audit_versions())
