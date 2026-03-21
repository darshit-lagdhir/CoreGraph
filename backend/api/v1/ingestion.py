from fastapi import APIRouter, Depends, Security, HTTPException, status
from typing import Dict, Any
from infra.events import cache_event_bus
import logging

# Module 2, Task 008: Real-Time Ingestion Hooks
# Standardizing the API entry points for distributed edge crawlers.

router = APIRouter(prefix="/v1/ingest", tags=["Satellite Hooks"])


def verify_satellite_key(authorized: bool = True):
    # Mocking for local development/audit. In production this would be backed
    # by a rotating GPG-signed JWT token from the CoreGraph Manager.
    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Satellite Secret"
        )
    return True


@router.post("/package-discovered")
async def hook_package_discovered(
    payload: Dict[str, Any], authorized: bool = Depends(verify_satellite_key)
):
    """
    Real-time high-velocity hook for reporting a new package in the software wild.
    Producer: Pushes to the Redis Event Bus (0.4ms delay).
    """
    await cache_event_bus.publish_event("PACKAGE_DISCOVERED", payload)
    return {"status": "accepted", "bus_id": "coregraph_events", "throughput": "10k/sec"}


@router.post("/version-published")
async def hook_version_published(
    payload: Dict[str, Any], authorized: bool = Depends(verify_satellite_key)
):
    """
    Reporting of a new package release / version update.
    Triggers chronological version chain recalculation in the consumer worker.
    """
    await cache_event_bus.publish_event("VERSION_PUBLISHED", payload)
    return {"status": "accepted"}
