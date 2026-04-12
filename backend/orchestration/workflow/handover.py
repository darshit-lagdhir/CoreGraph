import asyncio


class HandoverManifold:
    def __init__(self, max_size=64000):
        self.queue = asyncio.Queue(maxsize=max_size)

    async def submit(self, task: bytes):
        await self.queue.put(task)

    async def acquire(self):
        return await self.queue.get()
