import json
import os
import hashlib
import aiofiles
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict

class SimulationResolver:
    """
    The Dynamic Resolution Kernel for S.U.S.E. (Task 001).
    Now augmented with Bucketed Directory resolution for industrial-scale oceans.
    """
    def __init__(self, fixtures_path: str):
        self.fixtures_path = Path(fixtures_path)
        self.cache: Dict[str, dict] = {} # Simple memory cache for hot nodes
        self.max_cache_size = 1000 # LRU limit

    async def resolve_purl(self, ecosystem: str, name: str) -> Optional[dict]:
        """
        Intercepts PURL requests and resolves from the bucketed software ocean.
        """
        cache_key = f"{ecosystem}_{name}"

        # 1. Hot cache lookup (L3 Cache Emulation)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 2. Bucketed Path Resolution (Consistency with Generator)
        bucket = hashlib.md5(name.encode()).hexdigest()[:2]
        
        # Priority 1: Bucketed (Modern)
        fixture_file = self.fixtures_path / ecosystem / bucket / f"{name}.json"
        
        # Priority 2: Flat (Legacy Task 001 bootstrap)
        if not fixture_file.exists():
            fixture_file = self.fixtures_path / f"{ecosystem}_{name}.json"

        if not fixture_file.exists():
            return None

        try:
            async with aiofiles.open(fixture_file, mode='r') as f:
                content = await f.read()
                data = json.loads(content)

                # Simple LRU eviction logic
                if len(self.cache) >= self.max_cache_size:
                    evict_key = next(iter(self.cache))
                    del self.cache[evict_key]

                self.cache[cache_key] = data
                return data
        except Exception as e:
            # Operational fault in the synthetic ocean
            print(f"[RESO-FAULT] Corrupt or unreadable fixture: {fixture_file} - {e}")
            return None
