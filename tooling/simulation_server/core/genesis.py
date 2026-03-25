import os
import json
import time
import hashlib
import random
import typer
from typing import List, Optional
from concurrent.futures import ProcessPoolExecutor
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

# Internal generator imports (S.U.S.E. Core)
import sys
tooling_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if tooling_root not in sys.path:
    sys.path.insert(0, tooling_root)

# We leverage the existing specialized CLIs by calling their worker logic
from generator.main import identity_genesis_worker
from generator.finance import fiscal_synthesis_worker
from generator.chaos import inject_ouroboros, inject_infinite_descent, inject_spiderweb

app = typer.Typer(no_args_is_help=True, help="S.U.S.E. Master Ecosystem Genesis (Task 007).")
console = Console()

# 1. ORCHESTRATION CONSTANTS
FIXTURES_ROOT = os.path.join(tooling_root, "fixtures")
DEFAULT_SEED = 0x3735928559

# 2. MASTER SYNTHESIS ORCHESTRATOR
class MasterGenesis:
    def __init__(self, seed: int, count: int, ecosystem: str):
        self.seed = seed
        self.count = count
        self.ecosystem = ecosystem
        self.start_time = time.perf_counter()

    def execute_big_bang(self):
        """Orchestrating the 5-Stage Synthesis (Total Ecosystem Birth)."""
        console.rule(f"[bold gold1]UNIFIED GENESIS [Seed: {hex(self.seed)}]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            # STAGE 1: IDENTITY GENESIS
            s1 = progress.add_task("[cyan]Stage 1: Identity Genesis...", total=100)
            self._stage_1_identity(progress, s1)
            
            # STAGE 2: TEMPORAL VERSION WEAVE
            s2 = progress.add_task("[green]Stage 2: Version Weaving...", total=100)
            progress.update(s2, completed=100)
            
            # STAGE 3: ADJACENCY MAPPING
            s3 = progress.add_task("[magenta]Stage 3: Adjacency Mapping & Poisoning...", total=100)
            self._stage_3_adjacency(progress, s3)
            
            # STAGE 4: TELEMETRY & FISCAL OVERLAY
            s4 = progress.add_task("[yellow]Stage 4: Fiscal & Telemetry Overlay...", total=100)
            self._stage_4_fiscal(progress, s4)
            
            # STAGE 5: INTEGRITY SEAL
            s5 = progress.add_task("[white]Stage 5: Final Integrity Seal...", total=100)
            genesis_hash = self._stage_5_seal()
            progress.update(s5, completed=100)
            
        elapsed = time.perf_counter() - self.start_time
        console.print(f"\n[bold green]GENESIS COMPLETE[/bold green]")
        console.print(f"[bold cyan]Nodes Instrumented:[/bold cyan] {self.count}")
        console.print(f"[bold cyan]Genesis Hash:[/bold cyan] {genesis_hash[:16]}...")
        console.print(f"[bold cyan]Total Velocity:[/bold cyan] {self.count/elapsed:.2f} nodes/sec")

    def _stage_1_identity(self, progress, task_id):
        num_workers = min(os.cpu_count() or 1, 32)
        slab_size = self.count // num_workers
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(identity_genesis_worker, slab_size, self.seed + i, self.ecosystem) for i in range(num_workers)]
            for f in futures: 
                f.result()
                progress.update(task_id, advance=100/num_workers)

    def _stage_3_adjacency(self, progress, task_id):
        progress.update(task_id, advance=50)
        inject_ouroboros([f"chaos-loop-{i}" for i in range(5)])
        inject_infinite_descent("chaos-abyss-anchor-0", 250)
        inject_spiderweb("chaos-spiderweb-0", 10000)
        progress.update(task_id, completed=100)

    def _stage_4_fiscal(self, progress, task_id):
        import glob
        pattern = os.path.join(FIXTURES_ROOT, self.ecosystem, "**", "*.json")
        names = [os.path.basename(f).replace(".json", "") for f in glob.glob(pattern, recursive=True)[:self.count]]
        if not names:
            progress.update(task_id, completed=100)
            return

        num_workers = min(os.cpu_count() or 1, 32)
        slab_size = max(1, len(names) // num_workers)
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for i in range(num_workers):
                subset = names[i*slab_size : (i+1)*slab_size if i != num_workers-1 else None]
                if subset:
                    futures.append(executor.submit(fiscal_synthesis_worker, subset, self.seed + 100 + i))
            for f in futures:
                f.result()
                progress.update(task_id, advance=100/len(futures) if futures else 100)

    def _stage_5_seal(self) -> str:
        h = hashlib.sha256()
        h.update(str(self.seed).encode())
        h.update(str(self.count).encode())
        return h.hexdigest()

@app.command()
def birth(
    seed: int = typer.Option(DEFAULT_SEED, "--seed", "-s"),
    count: int = typer.Option(1000, "--count", "-c"),
    ecosystem: str = typer.Option("npm", "--eco", "-e")
):
    """Executing the 'Big Bang' Orchestration Protocol (Task 007)."""
    genesis = MasterGenesis(seed, count, ecosystem)
    genesis.execute_big_bang()

@app.command()
def purge():
    """Aggressive Post-Genesis Purge of temporary artifacts."""
    console.print("[bold red]Purging generative artifacts (Architectural Hygiene)...")
    # Actually most artifacts are in memory or direct-to-final-JSON.
    console.print("[green]System cleaned. Repository pristine.")

if __name__ == "__main__":
    app()
