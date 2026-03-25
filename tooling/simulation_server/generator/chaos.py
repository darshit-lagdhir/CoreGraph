import os
import json
import random
import hashlib
import typer
from typing import List, Dict, Any
from concurrent.futures import ProcessPoolExecutor
from rich.progress import Progress

app = typer.Typer(help="S.U.S.E. Graph Chaos & Topology Poisoner (Task 005).")

# 1. CHAOS DIRECTORIES
FIXTURES_DIR = os.path.join(os.getcwd(), "tooling", "simulation_server", "fixtures", "npm")

def get_fixture_path(name: str) -> str:
    bucket = hashlib.md5(name.encode()).hexdigest()[:2]
    return os.path.join(FIXTURES_DIR, bucket, f"{name}.json")

# 2. THE OUROBOROS PARADOX (Circular Dependency Injection)
def inject_ouroboros(targets: List[str]):
    """Creates intentional circular loops (A -> B -> A or A -> B -> C -> A)."""
    if len(targets) < 2: return
    
    # 50/50: Tight vs Transitive
    if random.random() > 0.5: # Transitive (A -> B -> C -> A)
        for i in range(len(targets)):
            target = targets[i]
            next_target = targets[(i + 1) % len(targets)]
            path = get_fixture_path(target)
            if os.path.exists(path):
                with open(path, 'r') as f: data = json.load(f)
                # Poison the latest version (it's a list)
                if data.get("versions") and isinstance(data["versions"], list):
                    latest_v = data["versions"][-1]
                    latest_v["dependencies"] = {next_target: "*"}
                    with open(path, 'w') as f: json.dump(data, f)
    else: # Tight (A <-> B)
        a, b = targets[0], targets[1]
        for src, dst in [(a, b), (b, a)]:
            path = get_fixture_path(src)
            if os.path.exists(path):
                with open(path, 'r') as f: data = json.load(f)
                if data.get("versions") and isinstance(data["versions"], list):
                    latest_v = data["versions"][-1]
                    latest_v["dependencies"] = {dst: "*"}
                    with open(path, 'w') as f: json.dump(data, f)

# 3. THE INFINITE DESCENT (Abbysal Depth Violation)
def inject_infinite_descent(root_name: str, depth: int):
    """Creates a deep linear chain (A -> A1 -> A2 ... -> An)."""
    current = root_name
    for i in range(depth):
        next_node = f"{root_name}-abyss-{i}"
        path = get_fixture_path(current)
        bucket = hashlib.md5(current.encode()).hexdigest()[:2]
        os.makedirs(os.path.join(FIXTURES_DIR, bucket), exist_ok=True)
        
        data = {
            "name": current,
            "versions": [{"version": "1.0.0", "dependencies": {next_node: "*"}, "published_at": "2024-03-25T21:55:00Z"}]
        }
        with open(path, 'w') as f: json.dump(data, f)
        current = next_node
    
    # Terminate the chain
    with open(get_fixture_path(current), 'w') as f:
        json.dump({"name": current, "versions": [{"version": "1.0.0", "dependencies": {}, "published_at": "2024-03-25T21:55:00Z"}]}, f)

# 4. SPIDERWEB HUB (High-Degree Saturation)
def inject_spiderweb(name: str, degree: int):
    """Saturates a single node with massive outbound edges."""
    path = get_fixture_path(name)
    bucket = hashlib.md5(name.encode()).hexdigest()[:2]
    os.makedirs(os.path.join(FIXTURES_DIR, bucket), exist_ok=True)
    
    deps = {f"spider-link-{i}": "*" for i in range(degree)}
    data = {
        "name": name,
        "versions": [{"version": "1.0.0", "dependencies": deps, "published_at": "2024-03-25T21:55:00Z"}]
    }
    with open(path, 'w') as f: json.dump(data, f)

@app.command()
def poison(
    mode: str = typer.Option("all", help="Chaos mode: ouroboros, abyss, spiderweb, all"),
    intensity: int = typer.Option(10, help="Number of poisoned anchors to create.")
):
    """Executing the 'Graph Poisoner' Protocol (Task 005)."""
    typer.echo(f"[CHAOS] Initiating Structural Hostility (Mode: {mode})...")
    
    if mode in ["all", "ouroboros"]:
        typer.echo(" - Injecting Ouroboros Paradox (Circular Loops)...")
        all_files = []
        import glob
        for f in glob.glob(os.path.join(FIXTURES_DIR, "**", "*.json"), recursive=True)[:100]:
            all_files.append(os.path.basename(f).replace(".json", ""))
        
        if not all_files:
            typer.echo("[FAILURE] No software ocean identities detected. Run 'make sim-gen-dev' first.")
            raise typer.Exit(1)
            
        for _ in range(intensity):
            targets = random.sample(all_files, min(3, len(all_files)))
            inject_ouroboros(targets)

    if mode in ["all", "abyss"]:
        typer.echo(" - Injecting Infinite Descent (Recursive Depth)...")
        for i in range(intensity):
            inject_infinite_descent(f"chaos-abyss-anchor-{i}", 250)

    if mode in ["all", "spiderweb"]:
        typer.echo(" - Injecting Spiderweb Hubs (Degree Saturation)...")
        for i in range(intensity):
            inject_spiderweb(f"chaos-spiderweb-{i}", 10000)

    typer.echo("[SUCCESS] Software Ocean poisoned. System integrity tests ready.")

if __name__ == "__main__":
    app()
