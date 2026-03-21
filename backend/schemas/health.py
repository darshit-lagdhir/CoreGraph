from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthCheckDetail(BaseModel):
    """Deep diagnostic signature for individual system dependencies."""

    status: str = Field(..., description="Component-level operational state (PASS/FAIL)")
    latency_ms: Optional[float] = Field(None, description="Measured response time in milliseconds")
    message: Optional[str] = Field(None, description="Diagnostic payload or error vector")


class HardwareTelemetry(BaseModel):
    """Real-time performance metrics for the i9-13980hx 24-core silicon and 16GB RAM."""

    cpu_percent: float = Field(..., description="Aggregated logical core utilization")
    memory_used_mb: float = Field(..., description="Resident Set Size (RSS) consumption")
    memory_available_mb: float = Field(
        ..., description="Unallocated system RAM under the WSL2 leash"
    )
    vram_used_mb: Optional[float] = Field(
        None, description="NVIDIA VRAM utilization for clustering GPU acceleration"
    )


class HealthResponse(BaseModel):
    """OSINT-standard diagnostic manifest for systemic vitality reporting."""

    status: str = Field(..., description="High-level system health indicator")
    version: str = Field(..., description="Application version from the Global Configuration")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="ISO-8601 temporal marker for the specific diagnostic pulse",
    )
    uptime_seconds: float = Field(..., description="Process lifecycle duration")
    checks: Dict[str, HealthCheckDetail] = Field(
        ..., description="Matrix of dependency-specific audits"
    )
    hardware: HardwareTelemetry = Field(
        ..., description="Hardware-level resource availability summary"
    )
