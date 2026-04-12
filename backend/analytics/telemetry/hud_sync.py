from .ocular_multiplexer import OcularMultiplexer

class HUDSynchronizer:
    def __init__(self, multiplexer: OcularMultiplexer):
        self.mux = multiplexer

    async def flush_to_network(self):
        async with self.mux.lock:
            payload = memoryview(self.mux.buffer)[:self.mux.cursor].tobytes()
            self.mux.cursor = 0
            return payload
