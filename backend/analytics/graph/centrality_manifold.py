from dal.repositories.risk_repo import AuthorityRepository
class HierarchicalRankingManifold:
    def __init__(self, repo: AuthorityRepository):
        self.repo = repo
    def compute_pagerank(self, node_count: int, iterations: int = 10, damping: float = 0.85):
        for it in range(iterations):
            for i in range(node_count):
                val = (1.0 - damping) + damping * (self.repo.get_score(i) + 0.01)
                self.repo.assign_score(i, val)
        return True
