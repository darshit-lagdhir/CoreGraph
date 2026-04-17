import httpx
from core.config import settings


class LiveGithubClient:
    """Uses real GITHUB_GRAPHQL_TOKEN to pull live repo metrics for forensic evaluation."""

    def __init__(self):
        self.token = settings.GITHUB_GRAPHQL_TOKEN.get_secret_value()
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        self.url = "https://api.github.com/graphql"
        self.client = httpx.AsyncClient(headers=self.headers, timeout=10.0)

    async def get_repo_stats(self, owner: str, repo: str) -> dict:
        """Runs an optimized GraphQL query against GitHub's live database."""
        if not self.token or self.token == "sk-dummy-token":
            return {"error": "Dummy token active. Check .env configurations."}

        query = """
        query($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                stargazerCount
                forkCount
                issues(states: OPEN) { totalCount }
            }
        }
        """
        payload = {"query": query, "variables": {"owner": owner, "repo": repo}}

        try:
            resp = await self.client.post(self.url, json=payload)
            if resp.status_code == 200:
                data = resp.json().get("data", {}).get("repository")
                if data:
                    return {
                        "stars": data.get("stargazerCount", 0),
                        "forks": data.get("forkCount", 0),
                        "issues": data.get("issues", {}).get("totalCount", 0),
                    }
            return {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self):
        await self.client.aclose()
