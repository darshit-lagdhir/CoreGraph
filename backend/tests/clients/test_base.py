import asyncio
import pytest
import respx
import httpx
import time

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from clients.base import ResilientClient, CircuitBreakerException

@pytest.mark.asyncio
@respx.mock
async def test_resilient_exponential_jitter():
    client = ResilientClient("https://api.github.com")
    
    route = respx.get("/rate-limit-test")
    route.side_effect = [
        httpx.Response(429, headers={"Retry-After": "2"}),
        httpx.Response(429, headers={"Retry-After": "2"}),
        httpx.Response(429, headers={"Retry-After": "2"}),
        httpx.Response(200, json={"status": "resolved"}),
    ]
    
    start_time = time.time()
    response = await client.request_node("GET", "/rate-limit-test")
    elapsed = time.time() - start_time
    
    assert response.status_code == 200
    assert response.json() == {"status": "resolved"}
    assert elapsed > 2.0
    await client.aclose()

@pytest.mark.asyncio
@respx.mock
async def test_circuit_breaker_suspension():
    client = ResilientClient("https://api.github.com")
    route = respx.get("/outage")
    route.side_effect = httpx.Response(500)
    
    with pytest.raises(httpx.HTTPStatusError):
        await client.request_node("GET", "/outage")
        
    with pytest.raises(CircuitBreakerException):
        await client.request_node("GET", "/outage")

    await client.aclose()
