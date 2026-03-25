import pytest
import os
import sys
from fastapi.testclient import TestClient

# Ensure simulation server root is in the path
root = os.getcwd()
sim_server_root = os.path.join(root, "tooling", "simulation_server")
if sim_server_root not in sys.path:
    sys.path.insert(0, sim_server_root)

from main import app

client = TestClient(app)

def test_simulation_health_probe():
    """
    S.U.S.E. Health & Ocean State Audit.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["ocean_state"] == "hardened"

def test_broad_fanout_fixture():
    """
    Validation of the 'synthetic-broad-core' (10,000 nodes).
    """
    response = client.get("/p/npm/synthetic-broad-core")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "synthetic-broad-core"
    deps = data["versions"][0]["dependencies"]
    assert len(deps) == 10000

def test_deep_abyss_fixture():
    """
    Validation of the 'synthetic-abyss-level-0' (100-level deep chain).
    """
    response = client.get("/p/npm/synthetic-abyss-level-0")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "synthetic-abyss-level-0"
    deps = data["versions"][0]["dependencies"]
    assert len(deps) == 1
    assert deps[0]["purl"] == "pkg:npm/synthetic-abyss-level-1@1.0.0"

def test_synthetic_404_resolution():
    """
    Validation of the 'Zero-Found' failure mode logic.
    """
    response = client.get("/p/npm/non-existent-vapourware")
    assert response.status_code == 404
