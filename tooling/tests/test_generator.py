import pytest
import os
import json
import hashlib
import glob
from datetime import datetime
from engine import DeterministicGenerator

# 1. SETUP: TARGETS
FIXTURES_DIR = os.path.join(os.getcwd(), "tooling", "simulation_server", "fixtures", "npm")

def test_deterministic_reproducibility():
    """
    Test 1: Master Seed Consistency.
    Verifies that the same seed produces identical nomenclature and version stacks.
    """
    start_date = datetime(2022, 1, 1)
    gen1 = DeterministicGenerator(0xABC)
    gen2 = DeterministicGenerator(0xABC)

    assert gen1.generate_name(100) == gen2.generate_name(100)

    v1 = gen1.generate_version_chain("test-pkg", 5, start_date)
    v2 = gen2.generate_version_chain("test-pkg", 5, start_date)

    assert [v["version"] for v in v1] == [v["version"] for v in v2]
    assert [v["published_at"] for v in v1] == [v["published_at"] for v in v2]

def test_semver_progression_audit():
    """
    Test 2: Procedural Evolution Integrity.
    Verifies that every generated version chain is strictly monotonic and SemVer compliant.
    """
    # Find all generated fixtures (limit to 100 for speed)
    fixtures = glob.glob(os.path.join(FIXTURES_DIR, "**", "*.json"), recursive=True)[:100]

    if not fixtures:
        pytest.skip("No fixtures found for audit. Run 'make sim-gen-dev' first.")

    for f_path in fixtures:
        with open(f_path, 'r') as f:
            data = json.load(f)

        versions = data["versions"]
        for i in range(len(versions) - 1):
            v_curr = versions[i]["version"]
            v_next = versions[i+1]["version"]

            # Basic Monotonic Verification
            curr_parts = [int(p) for p in v_curr.split(".")]
            next_parts = [int(p) for p in v_next.split(".")]

            assert next_parts > curr_parts, f"SemVer drift in {data['name']}: {v_next} <= {v_curr}"

            # Temporal Invariance
            t_curr = versions[i]["published_at"]
            t_next = versions[i+1]["published_at"]
            assert t_next > t_curr, f"Temporal drift in {data['name']}: {t_next} <= {t_curr}"

def test_zero_dangling_consistency():
    """
    Test 3: Adjacency Weaving Integrity.
    Verifies that all dependency pointers are resolvable from the fixture vault.
    """
    fixtures = glob.glob(os.path.join(FIXTURES_DIR, "**", "*.json"), recursive=True)[:20]

    # Pre-map all known identities (this is slow if millions, but we only check existence)
    known_identities = set()
    for f_path in glob.glob(os.path.join(FIXTURES_DIR, "**", "*.json"), recursive=True):
        known_identities.add(os.path.basename(f_path).replace(".json", ""))

    for f_path in fixtures:
        with open(f_path, 'r') as f:
            data = json.load(f)

        for v in data["versions"]:
            for dep in v["dependencies"]:
                # Dep purl: pkg:npm/name@version
                # name is after / and before @
                purl = dep["purl"]
                dep_name = purl.split("/")[-1].split("@")[0]
                assert dep_name in known_identities, f"Dangling pointer in {data['name']}: {dep_name} not found."
