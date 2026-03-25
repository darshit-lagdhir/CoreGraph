import os
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, Request, Response
from typing import Dict, Any
from pydantic import BaseModel

# Ensure we can import from the core/ and api/ folders within the simulation server root
import sys
server_root = os.path.dirname(os.path.abspath(__file__))
if server_root not in sys.path:
    sys.path.insert(0, server_root)

from core.resolver import SimulationResolver
from api.v4_github_graphql import handle_graphql_query
from api.finance_ledger import handle_funding_query
from core.chaos_manager import chaos_manager, ChaosRule

# 1. INITIALIZE S.U.S.E. APP (Task 001-006)
app = FastAPI(title="Standalone Universal Simulation Environment (S.U.S.E.) - Weaponized Edition")

# 2. RESOLUTION KERNEL BINDING (REST)
FIXTURES_PATH = os.path.join(server_root, "fixtures")
resolver = SimulationResolver(FIXTURES_PATH)

# 3. CHAOS CONFIGURATION INTERFACE (Judge-Ready Sabotage)
class ChaosConfigPayload(BaseModel):
    target: str # e.g., "global", "purl", "graphql", "funding"
    rule: ChaosRule

@app.put("/chaos/configure")
async def configure_chaos(payload: ChaosConfigPayload):
    """Hidden Administrative Entry Point for Sabotage Injection."""
    chaos_manager.set_rule(payload.target, payload.rule)
    return {"status": "configured", "chaos_active": True}

@app.delete("/chaos/clear")
async def clear_chaos():
    """Restores the Pristine Mirror State."""
    chaos_manager.clear_rules()
    return {"status": "restored", "chaos_active": False}

# 4. NETWORK ADVERSARY MIDDLEWARE (Chaos Gatekeeper)
@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    """
    S.U.S.E. Chaos Middleware: Intercepting and Degrading Network Responses.
    """
    # Bypass for configuration routes
    if "/chaos/" in request.url.path:
        return await call_next(request)

    # Resolve target from path
    target = "global"
    if "/p/" in request.url.path: target = "purl"
    elif "/graphql" in request.url.path: target = "graphql"
    elif "/funding/" in request.url.path: target = "funding"

    # Call Next (Generate Response)
    response = await call_next(request)
    
    # Extract data for chaos application (Basic Body/Headers)
    # Note: For simplicity, we wrap the response here or apply rules before.
    # To properly simulate packet drops/latency effectively, we often want pre-call logic.
    
    status, _, headers = await chaos_manager.apply_chaos(target, None)
    
    # 1. STATUS CODE DEGRADATION
    if status != 200:
        return Response(content="[CHAOS] Injected Network Failure.", status_code=status, headers=headers)
        
    return response

# 5. REST API ROUTING (Masquerading as deps.dev)
@app.get("/p/{ecosystem}/{name}")
async def resolve_package(ecosystem: str, name: str) -> Dict[str, Any]:
    result = await resolver.resolve_purl(ecosystem, name)
    if not result:
        raise HTTPException(status_code=404, detail="Synthetic package not found.")
    return result

# 6. GRAPHQL MASQUERADE (GITHUB V4)
@app.post("/graphql")
async def github_graphql(request: Request):
    return await handle_graphql_query(request)

# 7. FINANCIAL LEDGER MASQUERADE (FISCAL OSINT)
@app.get("/funding/{ecosystem}/{name}")
async def get_funding(ecosystem: str, name: str):
    return await handle_funding_query(ecosystem, name)

@app.get("/health")
async def simulation_health():
    return {"status": "operational", "ocean_state": "weaponized", "masquerade": "network_chaos_v1_active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
