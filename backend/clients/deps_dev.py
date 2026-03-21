import uuid
from typing import List, Dict, Any
from sqlalchemy.dialects.postgresql import insert

from database import AsyncSessionLocal
from models import Package, DependencyEdge
from clients.base import ResilientClient


class DepsDevClient:
    def __init__(self):
        self.api_client = ResilientClient(base_url="https://api.deps.dev")

    async def extract_ecosystem_topology(
        self, ecosystem: str, package_name: str
    ) -> List[uuid.UUID]:
        url = f"/v3/systems/{ecosystem}/packages/{package_name}/dependencies"
        response = await self.api_client.execute_request("GET", url)

        if response.status_code == 404:
            return []

        payload = response.json()
        nodes = payload.get("nodes", [])
        edges = payload.get("edges", [])

        package_inserts = []
        node_id_map: Dict[str, uuid.UUID] = {}

        for node in nodes:
            pkg_key = node.get("versionKey", {})
            pkg_system = pkg_key.get("system", ecosystem).upper()
            pkg_name = pkg_key.get("name")
            pkg_version = pkg_key.get("version")

            if not pkg_name:
                continue

            pkg_uuid = uuid.uuid4()
            node_id_map[pkg_name] = pkg_uuid

            package_inserts.append(
                {
                    "id": pkg_uuid,
                    "ecosystem": pkg_system,
                    "name": pkg_name,
                    "latest_version": pkg_version,
                    "description": None,
                    "license": None,
                }
            )

        edge_inserts = []
        for edge in edges:
            req = edge.get("requirement", "")
            source_name = edge.get("fromNode", {}).get("versionKey", {}).get("name", "")
            target_name = edge.get("toNode", {}).get("versionKey", {}).get("name", "")

            source_id = node_id_map.get(source_name)
            target_id = node_id_map.get(target_name)

            if source_id and target_id:
                edge_inserts.append(
                    {
                        "id": uuid.uuid4(),
                        "source_package_id": source_id,
                        "target_package_id": target_id,
                        "version_requirement": req,
                        "is_direct": edge.get("relation") == "DIRECT",
                    }
                )

        async with AsyncSessionLocal() as session:
            if package_inserts:
                stmt_pkg = insert(Package).values(package_inserts)
                stmt_pkg = stmt_pkg.on_conflict_do_nothing(index_elements=["ecosystem", "name"])
                await session.execute(stmt_pkg)

            if edge_inserts:
                stmt_edge = insert(DependencyEdge).values(edge_inserts)
                stmt_edge = stmt_edge.on_conflict_do_nothing()
                await session.execute(stmt_edge)

            await session.commit()

        await self.api_client.close()
        return list(node_id_map.values())
