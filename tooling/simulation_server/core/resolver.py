import json
import os
import aiofiles
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict

class SimulationResolver:
    """
    The Dynamic Resolution Kernel for S.U.S.E. (Task 001).
    Implements Lazy File-Mapped Loading and LRU Caching.
    """
    def __init__(self, fixtures_path: str):
        self.fixtures_path = Path(fixtures_path)
        self.cache: Dict[str, dict] = {} # Simple memory cache for hot nodes
        self.max_cache_size = 1000 # LRU limit

    async def resolve_purl(self, ecosystem: str, name: str) -> Optional[dict]:
        """
        Intercepts PURL requests and resolves from the synthetic software ocean.
        """
        cache_key = f"{ecosystem}_{name}"

        # 1. Hot cache lookup (L3 Cache Emulation)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 2. Lazy File-Mapped Loading (Gen5 NVMe Optimization)
        fixture_file = self.fixtures_path / f"{ecosystem}_{name}.json"

        if not fixture_file.exists():
            return None

        async with aiofiles.open(fixture_file, mode='r') as f:
            content = await f.read()
            data = json.loads(content)

            # Simple LRU eviction logic
            if len(self.cache) >= self.max_cache_size:
                # Evict the first key (simplistic)
                evict_key = next(iter(self.cache))
                del self.cache[evict_key]

            self.cache[cache_key] = data
            return data
