import os
import json
import base64
from typing import Dict, Any, List
from fastapi import Request, HTTPException
from core.ast_parser import analyze_query
from generator.engine import DeterministicGenerator

# Master Seed: Anchored at 0xDEADBEEF for total determinism
MASTER_SEED = 0xDEADBEEF
generator = DeterministicGenerator(MASTER_SEED)

async def handle_graphql_query(request: Request) -> Dict[str, Any]:
    """
    S.U.S.E. GitHub v4 GraphQL Masquerade (Task 003).
    Performs Intent Extraction and Dynamic Payload Synthesis.
    """
    body = await request.json()
    query_str = body.get("query", "")
    variables = body.get("variables", {})

    # 1. AST ANALYTICS (P-Core saturation via ASGI)
    analysis = analyze_query(query_str)

    if "error" in analysis and analysis["error"]:
        # Standard GraphQL Error Response
        return {"errors": [{"message": analysis["error"], "locations": []}]}

    response_data = {}
    aliases = analysis.get("aliases", {})

    # 2. DYNAMIC FIELD ASSEMBLY (Masquerade)
    for target in analysis["targets"]:
        pkg_name = target.get("name")
        repo_alias = target.get("target_alias", "repository")

        # Telemetry Synthesis via Seeded Engine
        telemetry = generator.generate_repo_telemetry(pkg_name or "synthetic-core")

        # Construct Selection Set matching requested intent
        # (Handling top-level aliases like forkCount -> forks)
        node_data = {
            "name": telemetry["name"],
            "stargazerCount": telemetry["stargazerCount"],
            aliases.get("forkCount", "forkCount"): telemetry["forkCount"],
            "isArchived": telemetry["isArchived"],
            "owner": telemetry["owner"],
            "defaultBranchRef": {
                "target": {
                    "history": {
                        "totalCount": int(telemetry["lambda_v"] * 36),
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": "Y29tbWl0X2VuZHBvaW50X3NpZ25hdHVyZQ=="
                        },
                        "edges": []
                    }
                }
            }
        }

        response_data[repo_alias] = node_data

    # 3. SCHEMA INTROSPECTION HANDLING (V4 Mirror)
    if "__schema" in analysis["fields"]:
        schema_path = os.path.join(os.getcwd(), "tooling", "simulation_server", "schemas", "github_v4_introspection.json")
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                return {"data": json.load(f)}

    return {"data": response_data}
