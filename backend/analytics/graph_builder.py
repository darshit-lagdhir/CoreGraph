import asyncio

import networkx as nx
from database import AsyncSessionLocal
from models import DependencyEdge, Package
from sqlalchemy import select


class GraphBuilder:
    def __init__(self, ecosystem: str):
        self.ecosystem = ecosystem
        self.graph = nx.DiGraph()

    async def build(self, db_session=None):
        """Constructs a cycle-free DAG from relational structures."""
        own_session = False
        if db_session is None:
            db_session = AsyncSessionLocal()
            own_session = True

        try:
            # 1. Fetch node metadata mapping structural indices for i9 performance limits
            pkg_result = await db_session.execute(
                select(Package).where(Package.ecosystem == self.ecosystem)
            )
            packages = pkg_result.scalars().all()

            for pkg in packages:
                self.graph.add_node(
                    str(pkg.id),
                    name=pkg.name,
                    ecosystem=pkg.ecosystem,
                    latest_version=pkg.latest_version,
                    # Base telemetry fields before analytical fusion
                    cvi=0,
                    pagerank=0.0,
                    blast_radius=0,
                )

            # 2. Map directed edges representing "Flow of Risk" boundaries
            dep_result = await db_session.execute(
                select(DependencyEdge)
                .join(Package, DependencyEdge.source_package_id == Package.id)
                .where(Package.ecosystem == self.ecosystem)
            )
            dependencies = dep_result.scalars().all()

            for dep in dependencies:
                # Direction: Dependent -> Dependency (Impact flows upward)
                self.graph.add_edge(str(dep.source_package_id), str(dep.target_package_id))

            # 3. DAG Enforcement Lifecycle: Detecting and Eliminating Circular Dependencies
            while True:
                try:
                    cycle = nx.find_cycle(self.graph, orientation="original")
                    # Severing the back-edge maintaining primary hierarchy
                    u, v, _ = cycle[0]
                    self.graph.remove_edge(u, v)
                    print(f"[ANALYTICS] Circular dependency eliminated: {u} -> {v}")
                except nx.NetworkXNoCycle:
                    break

            return self.graph

        finally:
            if own_session:
                await db_session.close()

    def get_graph(self):
        return self.graph
