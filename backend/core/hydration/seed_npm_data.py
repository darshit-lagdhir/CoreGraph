import asyncio
import httpx
import json
import os
import logging
from typing import List, Dict, Any
from backend.core.integrity.data_integrity_shield import DataIntegrityShield

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def fetch_top_npm_packages(count: int = 5000) -> List[Dict[str, Any]]:
    """
    Fetches real package data from the NPM Registry search API.
    """
    packages = []
    seen_names = set()
    page_size = 250
    pages = (count // page_size) + 1

    async with httpx.AsyncClient() as client:
        for i in range(pages):
            offset = i * page_size
            url = f"https://registry.npmjs.org/-/v1/search?text=score:>0.1&size={page_size}&from={offset}"
            logger.info(f"Fetching NPM packages from offset {offset}...")

            try:
                response = await client.get(url, timeout=60.0)
                if response.status_code == 429:
                    logger.warning("Rate limited. Sleeping 10s...")
                    await asyncio.sleep(10)
                    continue

                data = response.json()
                for obj in data.get("objects", []):
                    pkg = obj.get("package", {})
                    name = pkg.get("name")
                    if name in seen_names:
                        continue
                    seen_names.add(name)

                    packages.append(
                        {
                            "name": name,
                            "version": pkg.get("version"),
                            "description": pkg.get("description"),
                            "links": pkg.get("links"),
                            "publisher": pkg.get("publisher"),
                            "maintainers": pkg.get("maintainers"),
                            "keywords": pkg.get("keywords"),
                        }
                    )
                    if len(packages) >= count:
                        break
                if len(packages) >= count:
                    break

                # Sector Beta: Rate-Limit Avoidance
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error fetching page {i}: {e}")
                await asyncio.sleep(5)

    return packages


async def seed_npm_to_supabase(packages: List[Dict[str, Any]]):
    """
    Seeds the fetched NPM data into Supabase.
    """
    import asyncpg

    db_url = os.getenv("CLOUD_DATABASE_URL")
    if not db_url:
        logger.error("CLOUD_DATABASE_URL not found")
        return
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")

    logger.info(f"Igniting REAL NPM Hydration for {len(packages)} packages...")
    shield = DataIntegrityShield()

    try:
        conn = await asyncpg.connect(db_url)

        # 1. Clean Slate (Sector Kappa)
        await conn.execute("TRUNCATE nodes CASCADE")

        # Sector Eta: Integrity Shield Ignition
        batch_hash = shield.calculate_spectral_hash(packages)
        logger.info(f"[Eta] Spectral Checksum Generated: {batch_hash[:16]}...")

        # 2. Batch Insert
        records = []
        for i, pkg in enumerate(packages):
            node_id = pkg["name"]
            # Systemic Risk simulation based on package age/keywords (Sector Alpha)
            risk = 0.5 + (len(pkg.get("keywords", [])) * 0.05)
            metadata = {
                "version": pkg["version"],
                "description": pkg["description"],
                "publisher": pkg["publisher"],
                "keywords": pkg["keywords"],
            }
            # Topology Vector simulation (Sector Gamma)
            vector = [i / 5000.0, risk, 0.5]

            records.append((node_id, risk, json.dumps(metadata), vector))

        await conn.copy_records_to_table(
            "nodes", records=records, columns=["id", "risk_weight", "metadata", "topology_vector"]
        )

        logger.info(f"Successfully Hydrated {len(packages)} REAL NPM PACKAGES to Supabase.")
        await conn.close()
    except Exception as e:
        logger.error(f"NPM Hydration failed: {e}")


if __name__ == "__main__":

    async def main():
        pkgs = await fetch_top_npm_packages(5000)
        await seed_npm_to_supabase(pkgs)

    asyncio.run(main())
