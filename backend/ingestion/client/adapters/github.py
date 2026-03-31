import asyncio
import time
from typing import Dict, Any, AsyncGenerator

try:
    import ujson as json  # type: ignore[import-untyped]
except ImportError:
    import json

from .base import EcosystemAdapter

class GitHubAdapter(EcosystemAdapter):
    """
    Module 4 - Task 022: GitHub Source Scout.
    GraphQL-native recursive extraction ensuring Source-of-Truth tracking and 
    extreme rate-limit preservation.
    """
    __slots__ = ('_rate_limit_remaining', '_reset_time', '_hibernate_threshold')

    def __init__(self, client: Any):
        super().__init__(client)
        self._rate_limit_remaining = 5000
        self._reset_time = 0.0
        self._hibernate_threshold = 100

    async def extract_manifest(self, purl: str) -> AsyncGenerator[Dict[str, Any], None]:
        await self._enforce_pacing()
        
        parts = purl.replace('pkg:github/', '').split('/')
        if len(parts) < 2:
            return
        owner, repo = parts[0], parts[1].split('@')[0]

        query = self._build_graphql_query(owner, repo)
        payload = {"query": query}
        
        response = None
        if hasattr(self._client, 'execute_graphql'):
            response = await self._client.execute_graphql(payload)
            
        if not response:
            return
            
        self._parse_rate_limit(response.get('data', {}).get('rateLimit', {}))

        graphql_repo = response.get('data', {}).get('repository', {}) or {}
        releases = graphql_repo.get('releases', {}).get('nodes', [])
        
        for release in releases:
            actor = self.extract_actor_identity(release.get("author", {}))
            commit_data = release.get("tagCommit", {})
            signature_valid = commit_data.get("signature", {}).get("isValid", False) if commit_data.get("signature") else False
            
            yield {
                "name": f"{owner}/{repo}",
                "version": self.resolve_coordinates(release.get("tagName", "")),
                "actor": actor,
                "provenance": {
                    "commit_oid": commit_data.get("oid", ""),
                    "signature_verified": signature_valid
                }
            }

    def _parse_rate_limit(self, rl_data: Dict[str, Any]) -> None:
        if rl_data:
            self._rate_limit_remaining = rl_data.get('remaining', 5000)
            reset_at = rl_data.get('resetAt')
            # Real-world UTC ISO8601 parsing would occur here
            self._reset_time = time.time() + 3600 if reset_at else 0.0

    async def _enforce_pacing(self) -> None:
        """Dynamic Pacing Kernel preventing global IP blacklisting."""
        if self._rate_limit_remaining <= self._hibernate_threshold:
            now = time.time()
            if now < self._reset_time:
                wait_time = self._reset_time - now
                await asyncio.sleep(wait_time)
            self._rate_limit_remaining = 5000

    def _build_graphql_query(self, owner: str, repo: str) -> str:
        """Request Density Maximization minimizing total network round trips."""
        return f"""
        query {{
          rateLimit {{ remaining resetAt }}
          repository(owner: "{owner}", name: "{repo}") {{
            releases(first: 100, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
              nodes {{
                tagName
                createdAt
                author {{ login email }}
                tagCommit {{
                  oid
                  signature {{ isValid }}
                }}
              }}
            }}
          }}
        }}
        """

    def resolve_coordinates(self, dependency_string: str) -> str:
        """Universal Versioning shim mapping Semantic strings to Git references."""
        v = dependency_string.lower().strip()
        if v.startswith('v'):
            return v[1:]
        return v

    def extract_actor_identity(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts the underlying Social Actor to cross-reference PyPI/NPM ownership."""
        user = manifest.get('user', {}) if manifest else {}
        return {
            "name": manifest.get("login") or user.get("login", ""),
            "email": manifest.get("email") or user.get("email", ""),
            "ecosystem_id": "github"
        }
