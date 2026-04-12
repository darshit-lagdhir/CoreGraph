import struct
import asyncio


class OcularMultiplexer:
    def __init__(self, capacity=10485760):  # 10MB visual telemetry buffer
        self.buffer = bytearray(capacity)
        self.cursor = 0
        self.lock = asyncio.Lock()
        self.fmt = ">32sfff"  # NodeID, x, y, z (44 bytes total)
        self.record_size = struct.calcsize(self.fmt)

    async def broadcast_delta(self, node_id: bytes, x: float, y: float, z: float):
        async with self.lock:
            if self.cursor + self.record_size > len(self.buffer):
                self.cursor = 0  # Ring-buffer visual flush condition
            struct.pack_into(
                self.fmt, self.buffer, self.cursor, node_id.ljust(32, b"\x00"), x, y, z
            )
            self.cursor += self.record_size
            return self.cursor
