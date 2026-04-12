import struct


class QuadTreeManager:
    def __init__(self, engine):
        self.engine = engine
        self.root = engine.alloc()

    def insert(self, x, y, node_id):
        # Iterative insert avoiding recursive stack faults
        pass
