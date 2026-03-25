import json
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import List

def generate_broad_fanout(target_dir: str):
    """
    The 'Broad Fan-Out' Fixture (Task 001).
    1 root node -> 10,000 leaf nodes. Stresses the ingestion bus.
    """
    root_name = "synthetic-broad-core"
    leaf_count = 10000

    dependencies = []
    # Create the 10,000 leaf nodes first
    for i in range(1, leaf_count + 1):
        leaf_name = f"synthetic-leaf-{i}"
        leaf_data = {
            "name": leaf_name,
            "ecosystem": "npm",
            "versions": [{
                "version": "1.0.0",
                "published_at": datetime.now().isoformat(),
                "dependencies": [],
                "metadata": {"type": "leaf", "index": str(i)}
            }]
        }
        with open(os.path.join(target_dir, f"npm_{leaf_name}.json"), 'w') as f:
            json.dump(leaf_data, f)

        dependencies.append({
            "purl": f"pkg:npm/{leaf_name}@1.0.0",
            "requirement": "^1.0.0",
            "is_direct": True,
            "ecosystem": "npm"
        })

    # Create the root node
    root_data = {
        "name": root_name,
        "ecosystem": "npm",
        "versions": [{
            "version": "1.0.0",
            "published_at": datetime.now().isoformat(),
            "dependencies": dependencies,
            "metadata": {"type": "root", "fan_out": str(leaf_count)}
        }]
    }
    with open(os.path.join(target_dir, f"npm_{root_name}.json"), 'w') as f:
        json.dump(root_data, f)

def generate_deep_abyss(target_dir: str, depth: int = 100):
    """
    The 'Deep Abyss' Fixture (Task 001).
    Linear 100-level chain. Stresses recursive resolvers.
    """
    for d in range(depth):
        current_name = f"synthetic-abyss-level-{d}"
        next_name = f"synthetic-abyss-level-{d+1}"

        dependencies = []
        if d < depth - 1:
            dependencies.append({
                "purl": f"pkg:npm/{next_name}@1.0.0",
                "requirement": "1.0.0",
                "is_direct": True,
                "ecosystem": "npm"
            })

        pkg_data = {
            "name": current_name,
            "ecosystem": "npm",
            "versions": [{
                "version": "1.0.0",
                "published_at": datetime.now().isoformat(),
                "dependencies": dependencies,
                "metadata": {"depth": str(d)}
            }]
        }
        with open(os.path.join(target_dir, f"npm_{current_name}.json"), 'w') as f:
            json.dump(pkg_data, f)

if __name__ == "__main__":
    fixtures_path = os.path.join(os.getcwd(), "tooling", "simulation_server", "fixtures")
    os.makedirs(fixtures_path, exist_ok=True)
    print(f"[FIXTURE] Generating Broad Fan-Out in {fixtures_path}...")
    generate_broad_fanout(fixtures_path)
    print(f"[FIXTURE] Generating Deep Abyss (100 levels)...")
    generate_deep_abyss(fixtures_path)
    print("[SUCCESS] Synthetic Software Ocean Engineered.")
