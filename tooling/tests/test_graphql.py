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

def test_shadow_github_introspection():
    """
    Test 1: Introspection Schema Compliance.
    Verifies that S.U.S.E. mimics the structural footprint of GitHub v4.
    """
    query = "{ __schema { queryType { name } } }"
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "__schema" in data["data"]
    assert data["data"]["__schema"]["queryType"]["name"] == "Query"

def test_ast_alias_resolution():
    """
    Test 2: Deep Query Alias Mapping.
    Verifies the Masquerade Kernel correctly resolves multi-node aliases.
    """
    query = """
    {
      reactRepo: repository(owner: "facebook", name: "react") {
        stargazerCount
      }
      vueRepo: repository(owner: "vuejs", name: "vue") {
        stargazerCount
      }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "reactRepo" in data["data"]
    assert "vueRepo" in data["data"]
    assert data["data"]["reactRepo"]["stargazerCount"] > 0

def test_recursion_depth_protection():
    """
    Test 3: Recursive Fragment Stack Guard.
    Ensures S.U.S.E. rejects malformed 'Query Bombs' (Max Stack: 15).
    """
    # A manual 20-level nesting query
    query = "{ repository(name: \"r\") { " + "repository(name: \"r\") { " * 20 + " name " + " } " * 21 + " }"
    response = client.post("/graphql", json={"query": query})

    # S.U.S.E. returns a standard GraphQL Error array
    data = response.json()
    assert "errors" in data
    assert "Recursion" in data["errors"][0]["message"]

def test_synthetic_telemetry_fidelity():
    """
    Test 4: Repository Behavioral Signatures.
    Verifies that the Poisson/Zipfian engine provides realistic OSINT telemetry.
    """
    query = "{ repository(name: \"core-sync-999\") { stargazerCount forks: forkCount owner { login } } }"
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    node = response.json()["data"]["repository"]
    assert node["stargazerCount"] >= 1
    assert node["forks"] >= 0
    assert "synth-dev-" in node["owner"]["login"]
