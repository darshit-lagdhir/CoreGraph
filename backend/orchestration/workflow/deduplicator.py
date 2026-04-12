class TaskDeduplicator:
    def __init__(self):
        self.seen = set()
    def is_duplicate(self, sig: bytes) -> bool:
        if sig in self.seen: return True
        self.seen.add(sig)
        return False
