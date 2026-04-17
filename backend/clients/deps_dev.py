import httpx
import asyncio


class LiveDepsDevClient:
    """Live telemetry fetcher acting directly on Google's deps.dev API."""

    def __init__(self):
        self.base_url = "https://api.deps.dev/v3"
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def fetch_package_info(self, ecosystem: str, package_name: str):
        """Fetches live package data and its direct dependencies for the requested package."""
        # Clean ecosystem mapping (NPM -> npm, PyPI -> pypi)
        eco_map = {"npm": "NPM", "pypi": "PyPI", "crates": "Cargo", "go": "Go", "maven": "Maven"}
        mapped_eco = eco_map.get(ecosystem.lower(), "NPM")

        try:
            # Step 1: Get the package and its latest version
            pkg_response = await self.client.get(f"/systems/{mapped_eco}/packages/{package_name}")
            if pkg_response.status_code != 200:
                return {
                    "error": f"Package not found or API limits exceeded (HTTP {pkg_response.status_code})"
                }

            # Extract versions and find default
            data = pkg_response.json()
            versions = data.get("versions", [])
            if not versions:
                return {"error": "No associated versions located."}

            # Start with default or latest, if missing dependencies, fallback backwards
            default_version = next(
                (v.get("versionKey", {}).get("version") for v in versions if v.get("isDefault")),
                None,
            )
            if not default_version:
                default_version = versions[-1].get("versionKey", {}).get("version", "latest")

            target_list = [default_version] + [
                v.get("versionKey", {}).get("version") for v in reversed(versions[-20:])
            ]
            seen = set()

            dep_response = None
            target_version = default_version
            for ver in target_list:
                if not ver or ver in seen:
                    continue
                seen.add(ver)
                # Google deps.dev uses :dependencies
                resp = await self.client.get(
                    f"/systems/{mapped_eco}/packages/{package_name}/versions/{ver}:dependencies"
                )
                if resp.status_code == 200:
                    dep_response = resp
                    target_version = ver
                    break

            if dep_response and dep_response.status_code == 200:
                dep_data = dep_response.json()
                nodes = dep_data.get("nodes", [])

                # Transform to a clean format for the Tree View
                clean_deps = []
                for idx, node in enumerate(
                    nodes[1:15]
                ):  # Limit to first 14 deps so terminal doesn't overflow immediately
                    k = node.get("versionKey", {})
                    n = k.get("name", "Unknown")
                    v = k.get("version", "0.0.0")
                    clean_deps.append(f"{n}@{v}")

                return {
                    "ecosystem": mapped_eco,
                    "package": package_name,
                    "version": target_version,
                    "dependencies": clean_deps,
                    "links": data.get("versions", [-1])[-1].get("links", []) if versions else [],
                }
            else:
                return {
                    "error": f"Dependency resolution failed (HTTP {dep_response.status_code if dep_response else 404})"
                }

        except Exception as e:
            return {"error": f"Live Network Error: {str(e)}"}

    async def close(self):
        await self.client.aclose()
