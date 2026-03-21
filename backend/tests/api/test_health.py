import pytest
import time
import httpx
from main import app


@pytest.mark.asyncio
async def test_liveness_responsiveness():
    """Asserts that the /health/live endpoint returns 200 OK in under 10ms."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as ac:
        start_time = time.perf_counter()
        response = await ac.get("/health/live")
        latency = (time.perf_counter() - start_time) * 1000
        
        assert response.status_code == 200
        assert response.json()["status"] == "PASS"
        # We enforce sub-10ms responsiveness for the event loop liveness probe
        assert latency < 10.0


@pytest.mark.asyncio
async def test_readiness_dependency_chain():
    """Validates that the /health/ready endpoint performs deep diagnostic audits."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as ac:
        response = await ac.get("/health/ready")
        
        # In a healthy state, this should return 200
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PASS"
        assert "postgres" in data["checks"]
        assert "redis" in data["checks"]
        assert "hardware" in data


@pytest.mark.asyncio
async def test_latency_reporting_integrity():
    """Verifies that diagnostic latency metrics are correctly measured and reported."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as ac:
        response = await ac.get("/health/ready")
        data = response.json()
        
        # Latency should be a positive float reflecting the dependency audit duration
        assert data["checks"]["postgres"]["latency_ms"] > 0
        assert data["checks"]["redis"]["latency_ms"] > 0


@pytest.mark.asyncio
async def test_hardware_telemetry_normalization():
    """Asserts that the heartbeat returns accurate hardware metrics for the i9-13980hx."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as ac:
        response = await ac.get("/health/ready")
        hardware = response.json()["hardware"]
        
        # Validating logical core and memory metrics presence
        assert 0 <= hardware["cpu_percent"] <= 100
        assert hardware["memory_used_mb"] > 0
        assert hardware["memory_available_mb"] > 0
