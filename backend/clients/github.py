import uuid
import datetime
from typing import List, Dict, Any
from sqlalchemy.dialects.postgresql import insert

from config import settings
from database import AsyncSessionLocal
from models import MaintainerHealth
from clients.base import ResilientClient


class GitHubGraphQLClient:
    def __init__(self):
        headers = {
            "Authorization": f"Bearer {settings.GITHUB_GRAPHQL_TOKEN}",
            "Content-Type": "application/json",
        }
        self.api_client = ResilientClient(base_url="https://api.github.com", headers=headers)

    def _build_batch_query(self, packages: List[Dict[str, Any]]) -> str:
        query_fragments = []
        for index, pkg in enumerate(packages):
            repo_owner = pkg.get("owner")
            repo_name = pkg.get("repo_name")
            if not repo_owner or not repo_name:
                continue

            alias = f"repo_{index}"
            fragment = f"""
            {alias}: repository(owner: "{repo_owner}", name: "{repo_name}") {{
                url
                stargazerCount
                issues(states: OPEN) {{
                    totalCount
                }}
                defaultBranchRef {{
                    target {{
                        ... on Commit {{
                            history(first: 1) {{
                                edges {{
                                    node {{
                                        committedDate
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
                fundingLinks {{
                    platform
                    url
                }}
            }}
            """
            query_fragments.append(fragment)

        return "query {" + " ".join(query_fragments) + "}"

    async def ingest_telemetry_batch(self, packages: List[Dict[str, Any]]):
        if not packages:
            return

        query = self._build_batch_query(packages)
        response = await self.api_client.execute_request("POST", "/graphql", json={"query": query})

        if response.status_code != 200:
            return

        data = response.json().get("data", {})

        health_inserts = []
        for index, pkg in enumerate(packages):
            alias = f"repo_{index}"
            repo_data = data.get(alias)

            if not repo_data:
                continue

            dt_raw = None
            try:
                edges = repo_data["defaultBranchRef"]["target"]["history"]["edges"]
                if edges:
                    dt_raw = edges[0]["node"]["committedDate"]
            except (KeyError, TypeError):
                pass

            dt_obj = None
            if dt_raw:
                try:
                    dt_obj = datetime.datetime.fromisoformat(dt_raw.replace("Z", "+00:00"))
                except ValueError:
                    pass

            health_inserts.append(
                {
                    "id": uuid.uuid4(),
                    "package_id": pkg["package_id"],
                    "github_repo_url": repo_data.get("url"),
                    "commit_velocity_30d": 0,
                    "active_maintainers_count": 0,
                    "last_commit_timestamp": dt_obj,
                    "open_issues_count": repo_data.get("issues", {}).get("totalCount", 0),
                }
            )

        if health_inserts:
            async with AsyncSessionLocal() as session:
                stmt_health = insert(MaintainerHealth).values(health_inserts)
                stmt_health = stmt_health.on_conflict_do_nothing(index_elements=["package_id"])
                await session.execute(stmt_health)
                await session.commit()

        await self.api_client.close()
