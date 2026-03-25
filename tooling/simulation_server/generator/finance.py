import os
import json
import random
import hashlib
import typer
from typing import List, Dict, Any

app = typer.Typer(help="S.U.S.E. Financial Ledger Generator (Task 004).")

# 1. FISCAL CONFIGURATION
FIXTURES_DIR = os.path.join(os.getcwd(), "tooling", "simulation_server", "fixtures", "npm")

# 2. WORKER LOGIC (FOR ORCHESTRATION)
def fiscal_synthesis_worker(package_names: List[str], seed: int):
    """
    S.U.S.E. Fiscal Engine (Task 004).
    """
    random.seed(seed)
    
    currencies = ["USD", "EUR", "GBP", "JPY", "INR", "KWD", "CNY", "CHF"]
    
    for name in package_names:
        # 1. Deterministic Bucketing
        bucket = hashlib.md5(name.encode()).hexdigest()[:2]
        fixture_path = os.path.join(FIXTURES_DIR, bucket, f"{name}.json")
        
        if not os.path.exists(fixture_path):
            continue
            
        with open(fixture_path, 'r') as f:
            data = json.load(f)
            
        # 2. FISCAL OVERLAY (Leviathans vs Voids)
        is_leviathan = random.random() < 0.05 # 5% Leviathans
        
        funding = {
            "total_funding": random.randint(1000000, 500000000) if is_leviathan else random.randint(0, 10000),
            "currency": random.choice(currencies),
            "sponsors_count": random.randint(50, 1000) if is_leviathan else random.randint(0, 5),
            "fiscal_year": 2024
        }
        
        data["funding"] = funding
        
        with open(fixture_path, 'w') as f:
            json.dump(data, f)

@app.command()
def synthesize(
    seed: int = typer.Option(4242, help="Deterministic seed for fiscal randomization."),
    eco: str = typer.Option("npm", help="Target ecosystem.")
):
    """Executing the 'Financial Ledger' Protocol (Task 004)."""
    typer.echo(f"[FISCAL] Synthesizing funding for ecosystem: {eco}")
    
    # Collect all generated names
    import glob
    eco_dir = os.path.join(os.getcwd(), "tooling", "simulation_server", "fixtures", eco)
    names = [os.path.basename(f).replace(".json", "") for f in glob.glob(os.path.join(eco_dir, "**", "*.json"), recursive=True)]
    
    fiscal_synthesis_worker(names, seed)
    typer.echo(f"[SUCCESS] Financial ledger bonded to software ocean.")

if __name__ == "__main__":
    app()
