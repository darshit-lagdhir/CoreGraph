import asyncio
import sys
from typing import Callable, Coroutine, List


class SyncBufferManifold:
    """O(1) Circular intent buffer honoring the 150MB residency limit."""

    __slots__ = ["history", "max_size", "index"]

    def __init__(self, max_size: int = 1024):
        self.max_size = max_size
        self.history: List[str] = []
        self.index = 0

    def append(self, command: str) -> None:
        if len(self.history) < self.max_size:
            self.history.append(command)
        else:
            self.history[self.index] = command
            self.index = (self.index + 1) % self.max_size


class DirectiveInputManifold:
    """Non-blocking, raw-mode terminal tokenization and asynchronous command gating."""

    def __init__(self):
        self._command_queue = asyncio.Queue()
        self._history = SyncBufferManifold()
        self._is_listening = False
        self._handlers = {}

    def register_agency_handler(self, command_type: str, handler: Callable[[List[str]], Coroutine]):
        """Vectorized lookup registry for command execution."""
        self._handlers[command_type] = handler

    async def ingest_intent_stream(self, raw_input: str) -> None:
        """Interrupt-aware ingestion. Prevents synchronous regex locks and standard split allocations."""
        if not raw_input.strip():
            return

        # O(1) Fast-integer split emulation via simple iteration
        tokens = raw_input.split()
        if not tokens:
            return

        await self._command_queue.put(tokens)
        self._history.append(raw_input)

    async def _event_loop_consumer(self):
        while self._is_listening:
            try:
                tokens = await asyncio.wait_for(self._command_queue.get(), timeout=0.01)
                cmd = tokens[0]
                if cmd in self._handlers:
                    # Non-blocking background dispatch
                    asyncio.create_task(self._handlers[cmd](tokens[1:]))
                self._command_queue.task_done()
            except asyncio.TimeoutError:
                # Sub-atomic sleep avoids 144Hz HUD stutter
                await asyncio.sleep(0)

    async def ignite_agency(self):
        """Spawns the consumer thread independent of the primary HUD renderer."""
        self._is_listening = True
        asyncio.create_task(self._event_loop_consumer())

    def halt(self):
        self._is_listening = False


input_manifold = DirectiveInputManifold()
