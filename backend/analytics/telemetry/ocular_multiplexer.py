import struct
import asyncio

class SemanticMultiplexer:
    """ The Semantic Multiplexer: Packs pure analytics (entropy, mass, risk_idx) instead of coordinates. """
    def __init__(self, capacity=10485760):
        self.buffer = bytearray(capacity)
        self.cursor = 0
        self.lock = asyncio.Lock()
        # NodeID, entropy, risk_idx, centrality (Headless semantic metrics vs WebGL coordinates)
        self.fmt = ">32sfff"
        self.record_size = struct.calcsize(self.fmt)

    async def broadcast_delta(self, node_id: bytes, entropy: float, risk_idx: float, centrality: float):
        async with self.lock:
            if self.cursor + self.record_size > len(self.buffer):
                self.cursor = 0
            struct.pack_into(
                self.fmt, self.buffer, self.cursor, node_id.ljust(32, b"\x00"), entropy, risk_idx, centrality
            )
            self.cursor += self.record_size
            return self.cursor

