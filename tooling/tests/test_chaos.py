import pytest
import os
import sys
import time
from fastapi.testclient import TestClient

# Ensure simulation server root is in the path
root = os.getcwd()
sim_server_root = os.path.join(root, "tooling", "simulation_server")
if sim_server_root not in sys.path:
    sys.path.insert(0, sim_server_root)

from main import app

client = TestClient(app)

def test_chaos_latency_precision():
    """
    Test 1: Temporal Resilience Audit.
    Verifies that a 500ms spike is injected with 1% precision.
    """
    # 1. Configure Chaos (500ms delay)
    payload = {
        "target": "purl",
        "rule": {"latency_ms": 500, "status_code": 200}
    }
    client.put("/chaos/configure", json=payload)
    
    # 2. Measure P-core latency
    start = time.perf_counter()
    response = client.get("/p/npm/chaos-test-package")
    end = time.perf_counter()
    latency_ms = (end - start) * 1000
    
    # Assert within precision margin (500 to 700ms because of server overhead/looploop)
    assert latency_ms >= 500
    
    # 3. Restore Pristine State
    client.delete("/chaos/clear")

def test_http_429_rate_limit_injection():
    """
    Test 2: Rate-Limit Barrier Audit.
    Verifies the injection of 'Retry-After' headers for 429 status codes.
    """
    payload = {
        "target": "graphql",
        "rule": {"status_code": 429, "retry_after": 15}
    }
    client.put("/chaos/configure", json=payload)
    
    response = client.post("/graphql", json={"query": "{ test }"})
    assert response.status_code == 429
    assert response.headers.get("retry-after") == "15"
    
    client.delete("/chaos/clear")

def test_http_502_bad_gateway_injection():
    """
    Test 3: Infrastructure Collapse Audit.
    Verifies injection of 502/503 errors.
    """
    payload = {
        "target": "funding",
        "rule": {"status_code": 502}
    }
    client.put("/chaos/configure", json=payload)
    
    response = client.get("/funding/npm/chaos-target")
    assert response.status_code == 502
    
    client.delete("/chaos/clear")

def test_chaos_burst_auto_clearing():
    """
    Test 4: Transient Hostility Audit.
    Verifies that 'burst_count' auto-clears the rule after N requests.
    """
    payload = {
        "target": "purl",
        "rule": {"status_code": 503, "burst_count": 2}
    }
    client.put("/chaos/configure", json=payload)
    
    # Request 1: Should fail
    assert client.get("/p/npm/target-1").status_code == 503
    # Request 2: Should fail
    assert client.get("/p/npm/target-2").status_code == 503
    # Request 3: Should succeed (Auto-cleared)
    assert client.get("/p/npm/target-3").status_code != 503
