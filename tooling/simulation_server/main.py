import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from typing import Dict, Any

# Ensure we can import from the core/ and api/ folders within the simulation server root
import sys
server_root = os.path.dirname(os.path.abspath(__file__))
if server_root not in sys.path:
    sys.path.insert(0, server_root)

from core.resolver import SimulationResolver
from api.v4_github_graphql import handle_graphql_query
from api.finance_ledger import handle_funding_query

# 1. INITIALIZE S.U.S.E. APP (Task 001-004)
app = FastAPI(title="Standalone Universal Simulation Environment (S.U.S.E.)")

# 2. RESOLUTION KERNEL BINDING (REST)
FIXTURES_PATH = os.path.join(server_root, "fixtures")
resolver = SimulationResolver(FIXTURES_PATH)

# 3. REST API ROUTING (Masquerading as deps.dev)
@app.get("/p/{ecosystem}/{name}")
async def resolve_package(ecosystem: str, name: str) -> Dict[str, Any]:
    result = await resolver.resolve_purl(ecosystem, name)
    if not result:
        raise HTTPException(status_code=404, detail="Synthetic package not found.")
    return result

# 4. GRAPHQL MASQUERADE (GITHUB V4)
@app.post("/graphql")
async def github_graphql(request: Request):
    return await handle_graphql_query(request)

# 5. FINANCIAL LEDGER MASQUERADE (FISCAL OSINT)
@app.get("/funding/{ecosystem}/{name}")
async def get_funding(ecosystem: str, name: str):
    """
    Shadow Fiscal Infrastructure Entry Point.
    Intercepts and masquerades financial backing data across ISO 4217 currencies.
    """
    return await handle_funding_query(ecosystem, name)

@app.get("/health")
async def simulation_health():
    """Liveness probe for the simulation environment."""
    return {"status": "operational", "ocean_state": "hardened", "masquerade": "fiscal_v1_active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
