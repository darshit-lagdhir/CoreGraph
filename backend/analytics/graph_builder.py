import networkx as nx
from typing import AsyncGenerator, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Package, DependencyEdge, MaintainerHealth, FinancialHealth
from database import AsyncSessionLocal

async def stream_ecosystem_nodes(ecosystem: str) -> AsyncGenerator[Dict[str, Any], None]:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Package, MaintainerHealth, FinancialHealth)
            .outerjoin(MaintainerHealth, Package.id == MaintainerHealth.package_id)
            .outerjoin(FinancialHealth, Package.id == FinancialHealth.package_id)
            .where(Package.ecosystem == ecosystem)
        )
        result = await session.stream(stmt)
        async for row in result:
            pkg, m_health, f_health = row
            yield {
                "id": str(pkg.id),
                "name": pkg.name,
                "latest_version": pkg.latest_version,
                "maintainers": m_health.active_maintainers_count if m_health else 0,
                "last_commit": m_health.last_commit_timestamp.isoformat() if m_health and m_health.last_commit_timestamp else None,
                "budget": f_health.annual_budget_usd if f_health else 0.0,
                "is_commercially_backed": f_health.is_commercially_backed if f_health else False
            }

async def stream_ecosystem_edges(ecosystem: str) -> AsyncGenerator[Dict[str, str], None]:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(DependencyEdge.source_package_id, DependencyEdge.target_package_id)
            .join(Package, Package.id == DependencyEdge.source_package_id)
            .where(Package.ecosystem == ecosystem)
        )
        result = await session.stream(stmt)
        async for row in result:
            yield {
                "source": str(row[0]),
                "target": str(row[1])
            }

async def build_acyclic_graph(ecosystem: str) -> nx.DiGraph:
    G = nx.DiGraph()
    
    async for node in stream_ecosystem_nodes(ecosystem):
        G.add_node(
            node["id"],
            name=node["name"],
            budget=node["budget"],
            maintainers=node["maintainers"],
            last_commit=node["last_commit"],
            is_commercially_backed=node["is_commercially_backed"]
        )
        
    async for edge in stream_ecosystem_edges(ecosystem):
        G.add_edge(edge["source"], edge["target"])

    cycles = list(nx.simple_cycles(G))
    for cycle in cycles:
        if len(cycle) >= 2:
            G.remove_edge(cycle[-1], cycle[0])
            
    return G
