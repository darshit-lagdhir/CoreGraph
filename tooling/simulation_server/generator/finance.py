import os
import json
import random
import hashlib
import typer
from typing import Dict, Any, List
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from engine import DeterministicGenerator
from core.currency_vault import CURRENCY_VAULT, get_currency_exponent

# Initialize CLI
app = typer.Typer(help="S.U.S.E. Financial Ledger Generator (Task 004).")

# 1. GENERATION CONSTANTS
FINANCE_FIXTURES_DIR = os.path.join(os.getcwd(), "tooling", "simulation_server", "fixtures", "finance")

# 2. SEED-AWARE WORKER (FISCAL SYNTHESIS)
def fiscal_synthesis_worker(pkg_names: List[str], master_seed: int):
    """
    Simulates the Fiscal Universe (Matthew Effect, Leviathans, Void).
    """
    generator = DeterministicGenerator(master_seed)
    # List of available ISO codes
    currency_codes = list(CURRENCY_VAULT.keys())

    for pkg_name in pkg_names:
        sub_seed = generator.get_sub_seed(pkg_name)
        state = random.Random(sub_seed)

        # Determine Fiscal Profile: Leviathan (0.5%), standard, or Void (45%)
        profile_roll = state.random()

        ledger_entries = []
        is_leviathan = profile_roll < 0.005 # 0.5% probability
        is_void = 0.005 <= profile_roll < 0.455 # 45% probability

        if not is_void: # Populated Projects
            # Number of funding sources
            source_count = state.randint(5, 50) if is_leviathan else state.randint(1, 5)

            for _ in range(source_count):
                # Deterministic Currency Choice (70% non-USD for funded projects)
                currency = "USD" if state.random() > 0.70 else state.choice(currency_codes)
                exponent = get_currency_exponent(currency)

                # Boundary Stressing: Leviathans receive 9-figure fundings
                amount_base = state.uniform(100.0, 5000.0)
                if is_leviathan:
                    amount_base = state.uniform(1000000.0, 100000000.0)

                # Format to specific exponent precision (Fixed-Point Emulation)
                formatted_amount = f"{amount_base:.{exponent}f}"

                # Injection of "Dirty Data" (commas, symbols in string)
                if state.random() < 0.10: # 10% dirty
                    formatted_amount = f"{CURRENCY_VAULT[currency].symbol}{formatted_amount}"
                if state.random() < 0.05: # Comma pollution
                    formatted_amount = formatted_amount.replace(".", ",")

                ledger_entries.append({
                    "provider": state.choice(["opencollective", "github_sponsors", "lfx", "sovereign_grant"]),
                    "currency": currency,
                    "amount": formatted_amount,
                    "status": "cleared" if state.random() > 0.05 else "refunded",
                    "timestamp": "2024-03-25T21:44:00Z"
                })

            # Anti-Matter Ledger Simulation (Negative balances for 1% of funded projects)
            if state.random() < 0.02:
                ledger_entries.append({
                    "provider": "audit_penalty",
                    "currency": "USD",
                    "amount": f"-{state.randint(1000, 50000)}.00",
                    "status": "clawback"
                })

        fixture_data = {
            "name": pkg_name,
            "total_balance_normalized_usd": "0.00", # Application must calculate this!
            "ledger": ledger_entries,
            "profile": "leviathan" if is_leviathan else "ghost" if is_void else "standard"
        }

        # Bucketed Directory Strategy (MD5 for dual consistency)
        bucket = hashlib.md5(pkg_name.encode()).hexdigest()[:2]
        bucket_dir = os.path.join(FINANCE_FIXTURES_DIR, bucket)
        os.makedirs(bucket_dir, exist_ok=True)

        with open(os.path.join(bucket_dir, f"{pkg_name}.json"), 'w') as f:
            json.dump(fixture_data, f)

# 3. CLI COMMAND DEFINITION
@app.command()
def generate(
    seed: int = typer.Option(0xDEADBEEF, "--seed", "-s", help="Master deterministic seed."),
    count: int = typer.Option(100, "--count", "-c", help="Number of packages to synthesize finances for.")
):
    """Executing the 'Master Accountant' Synthesis (Task 004)."""
    os.makedirs(FINANCE_FIXTURES_DIR, exist_ok=True)

    # We must scan existing software ocean identities to populate
    source_fixtures = os.path.join(os.getcwd(), "tooling", "simulation_server", "fixtures", "npm")
    names = []
    import glob
    for f in glob.glob(os.path.join(source_fixtures, "**", "*.json"), recursive=True)[:count]:
        names.append(os.path.basename(f).replace(".json", ""))

    if not names:
        typer.echo("[FAILURE] No software ocean identities detected. Run 'make sim-gen-dev' first.")
        raise typer.Exit(1)

    num_workers = min(os.cpu_count() or 1, 24)
    slab_size = len(names) // num_workers

    with Progress() as progress:
        task = progress.add_task("[yellow]Fiscal Synthesis (ISO 4217)", total=len(names))
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for i in range(num_workers):
                subset = names[i * slab_size : i * slab_size + slab_size if i != num_workers-1 else None]
                futures.append(executor.submit(fiscal_synthesis_worker, subset, seed))

            for f in futures:
                f.result()
                progress.update(task, advance=slab_size)

    typer.echo(f"[SUCCESS] Financial Ocean populated for {len(names)} packages.")

if __name__ == "__main__":
    app()
