from backend.ingestion.persistence.linkage import LinkageManifold
class GraphAggregator:
    def __init__(self, capacity=3810000):
        self.linkage = LinkageManifold(capacity)
    def unify(self, ns: str, name: str) -> int:
        return self.linkage.resolve_entity(ns, name)
