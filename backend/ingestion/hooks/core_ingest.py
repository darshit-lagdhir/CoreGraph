import asyncio
import httpx
import json
import random
import time
import glob
from typing import List, Dict, Any, Optional

# Internal CoreGraph imports (Task 027 persistent paths)
import sys
import os
root = os.getcwd()
if root not in sys.path:
    sys.path.insert(0, root)

class IngestionHookKernel:
    """
    S.U.S.E. Ingestion Hook Kernel (Task 008).
    High-concurrency, asynchronous gateway for the 3.84M node software ocean.
    """
    def __init__(self, base_url: str = "http://localhost:8081", batch_size: int = 100):
        self.base_url = base_url
        self.batch_size = batch_size
        self.client = httpx.AsyncClient(timeout=30.0, limits=httpx.Limits(max_connections=500))
        self.nodes_processed = 0
        self.quarantined = 0
        self.start_time = time.perf_counter()

    async def fetch_and_validate(self, ecosystem: str, name: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/p/{ecosystem}/{name}"
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                if not all(k in data for k in ["name", "versions"]): return None
                return data
            self.quarantined += 1
            return None
        except Exception:
            self.quarantined += 1
            return None

    async def ingest_stream(self, purl_generator):
        tasks = []
        async for purl in purl_generator:
            ecosystem, name = self._parse_purl(purl)
            tasks.append(self.fetch_and_validate(ecosystem, name))
            if len(tasks) >= self.batch_size:
                results = await asyncio.gather(*tasks)
                self._process_batch([r for r in results if r])
                tasks = []
        if tasks:
            results = await asyncio.gather(*tasks)
            self._process_batch([r for r in results if r])

    def _process_batch(self, batch: List[Dict[str, Any]]):
        if not batch: return
        self.nodes_processed += len(batch)
        elapsed = time.perf_counter() - self.start_time
        velocity = self.nodes_processed / elapsed if elapsed > 0 else 0
        print(f"[INGEST] Processed: {self.nodes_processed} | Velocity: {velocity:.2f} nodes/sec | Quarantined: {self.quarantined}")

    def _parse_purl(self, purl: str) -> tuple[str, str]:
        parts = purl.replace("pkg:", "").split("/")
        return parts[0], parts[1]

    async def close(self):
        await self.client.aclose()

async def run_benchmark(limit: int = 500):
    kernel = IngestionHookKernel(batch_size=50)
    fixture_dir = os.path.join(root, "tooling", "simulation_server", "fixtures", "npm")
    
    pattern = os.path.join(fixture_dir, "**", "*.json")
    all_files = glob.glob(pattern, recursive=True)
    print(f"[DEBUG] Found {len(all_files)} total fixtures.")
    
    async def purl_gen():
        count = 0
        for f in all_files:
            if count >= limit: break
            name = os.path.basename(f).replace(".json", "")
            yield f"pkg:npm/{name}"
            count += 1

    print(f"[COREGRAPH] Launching Ingestion Benchmark (Real Nodes)...")
    await kernel.ingest_stream(purl_gen())
    await kernel.close()

if __name__ == "__main__":
    asyncio.run(run_benchmark(100)) # Quick test with 100 nodes
