class BinaryPartitionRepo:
    def __init__(self):
        self._shards = {}
    def shard_vertex(self, vertex_id: bytes, tile_sig: bytes):
        if tile_sig not in self._shards:
            self._shards[tile_sig] = bytearray()
        self._shards[tile_sig].extend(vertex_id)
    def get_shard(self, tile_sig: bytes) -> bytes:
        return self._shards.get(tile_sig, b'')
