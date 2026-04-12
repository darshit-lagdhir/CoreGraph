import time, struct


class TemporalVersionRepo:
    def __init__(self):
        self._versions = {}

    def stamp(self, node_id: bytes) -> bytes:
        ts_bytes = struct.pack("d", time.time())
        self._versions[node_id] = ts_bytes
        return ts_bytes

    def verify(self, node_id: bytes, ts_bytes: bytes) -> bool:
        return self._versions.get(node_id) == ts_bytes
