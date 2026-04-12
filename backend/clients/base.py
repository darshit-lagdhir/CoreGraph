import struct
import asyncio


class BinaryTransportPhalanx:
    def __init__(self, buffer_size=10485760):  # 10MB intake buffer
        self.intake_buffer = bytearray(buffer_size)
        self.cursor = 0
        self.lock = asyncio.Lock()
        # Struct: 32s (node_id), Q (timestamp), H (status_code), I (payload_size)
        self.header_fmt = ">32sQHI"
        self.header_size = struct.calcsize(self.header_fmt)

    async def ingest_payload(self, node_id: bytes, timestamp: int, status: int, payload: bytes):
        async with self.lock:
            l = len(payload)
            req_size = self.header_size + l
            if self.cursor + req_size > len(self.intake_buffer):
                self.cursor = 0  # Circular reset for continuous high-throughput ingestion

            struct.pack_into(
                self.header_fmt,
                self.intake_buffer,
                self.cursor,
                node_id.ljust(32, b"\x00"),
                timestamp,
                status,
                l,
            )
            self.intake_buffer[
                self.cursor + self.header_size : self.cursor + self.header_size + l
            ] = payload
            self.cursor += req_size
            return self.cursor
