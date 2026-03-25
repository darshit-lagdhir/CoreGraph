import os
import json
import random
import typer
import aiofiles
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
import hashlib
from engine import DeterministicGenerator

# Initialize Typer CLI
app = typer.Typer(help="S.U.S.E. Fixture Generator: Producing the Procedural Software Ocean.")

# 1. GENERATION CONSTANTS
FIXTURES_DIR = os.path.join(os.getcwd(), "tooling", "simulation_server", "fixtures")

# 2. SEED-AWARE WORKER (IDENTITY GENESIS)
def identity_genesis_worker(slave_id: int, start_idx: int, count: int, master_seed: int, ecosystem: str):
    """
    PASS 1: Identity Genesis.
    Generating all package names and version skeletons.
    """
    generator = DeterministicGenerator(master_seed)
    local_fixtures = []

    for i in range(count):
        idx = start_idx + i
        pkg_name = f"{ecosystem}-{generator.generate_name(idx)}"

        # Consistent Version History
        versions = generator.generate_version_chain(pkg_name, random.randint(1, 15), datetime(2022, 1, 1))

        pkg_data = {
            "name": pkg_name,
            "ecosystem": ecosystem,
            "versions": versions
        }

        # Determine Bucket (256 folders for Gen5 NVMe optimization)
        bucket_hash = hashlib.md5(pkg_name.encode()).hexdigest()
        bucket = bucket_hash[:2]
        bucket_dir = os.path.join(FIXTURES_DIR, ecosystem, bucket)
        os.makedirs(bucket_dir, exist_ok=True)

        fixture_path = os.path.join(bucket_dir, f"{pkg_name}.json")
        with open(fixture_path, 'w') as f:
            json.dump(pkg_data, f)

        local_fixtures.append(pkg_name)

    return local_fixtures

# 3. ADJACENCY WEAVING WORKER (PASS 2)
def adjacency_weaving_worker(pkg_names: List[str], all_identities: List[str], master_seed: int, ecosystem: str):
    """
    PASS 2: Adjacency Weaving.
    Assigning Zipfian pointers ensuring Zero-Dangling consistency.
    """
    generator = DeterministicGenerator(master_seed)

    for pkg_name in pkg_names:
        # Load identity genesis fixture
        bucket_hash = hashlib.md5(pkg_name.encode()).hexdigest()
        bucket = bucket_hash[:2]
        fixture_path = os.path.join(FIXTURES_DIR, ecosystem, bucket, f"{pkg_name}.json")

        with open(fixture_path, 'r') as f:
            data = json.load(f)

        # Assign Dependencies for each version
        # Zipfian model: top packages become foundation nodes (Hubs)
        for version in data["versions"]:
            # Standard entropy: 1-5 dependencies
            dep_count = random.randint(1, 5)
            # Choose from all_identities ensuring hierarchy resolution
            selected = random.sample(all_identities, min(dep_count, len(all_identities)))

            version["dependencies"] = [
                {
                    "purl": f"pkg:{ecosystem}/{s_name}@1.0.0",
                    "requirement": "^1.0.0",
                    "is_direct": True,
                    "ecosystem": ecosystem
                } for s_name in selected if s_name != pkg_name
            ]

        with open(fixture_path, 'w') as f:
            json.dump(data, f)

# 4. CLI COMMAND DEFINITIONS
@app.command()
def generate(
    count: int = typer.Option(100, "--count", "-c", help="Total Package Identity count."),
    seed: int = typer.Option(0xDEADBEEF, "--seed", "-s", help="Master deterministic seed."),
    ecosystem: str = typer.Option("npm", "--eco", "-e", help="The target software ecosystem.")
):
    """
    Industrial generation of the software universe (Task 002).
    Saturates i9 Performance Cores (Slabs Allocation).
    """
    os.makedirs(FIXTURES_DIR, exist_ok=True)

        # console=typer.get_app_dir("cg-sim-gen")

    with Progress() as progress:
        # STEP 1: IDENTITY GENESIS (24-Core Parallel)
        task1 = progress.add_task("[green]Genesis (Identities)", total=count)

        num_workers = min(os.cpu_count() or 1, 24)
        slab_size = count // num_workers

        all_names = []
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for i in range(num_workers):
                c = slab_size + (count % num_workers if i == num_workers -1 else 0)
                futures.append(executor.submit(identity_genesis_worker, i, i * slab_size, c, seed, ecosystem))

            for f in futures:
                all_names.extend(f.result())
                progress.update(task1, advance=slab_size)

        # STEP 2: ADJACENCY WEAVING (Zero-Dangling Verification)
        task2 = progress.add_task("[cyan]Weaving (Dependencies)", total=len(all_names))

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            slab_size = len(all_names) // num_workers
            futures = []
            for i in range(num_workers):
                c = slab_size + (len(all_names) % num_workers if i == num_workers -1 else 0)
                subset = all_names[i * slab_size : i * slab_size + c]
                futures.append(executor.submit(adjacency_weaving_worker, subset, all_names, seed, ecosystem))

            for f in futures:
                f.result()
                progress.update(task2, advance=slab_size)

    typer.echo(f"[SUCCESS] {count} Identites with {len(all_names)} fixtures finalized.")

if __name__ == "__main__":
    app()
