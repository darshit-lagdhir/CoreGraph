from pydantic import BaseModel, Field
from typing import Dict, Any

class KernelVitals(BaseModel):
    status: str = Field(..., description="Operational status: ONLINE, DEGRADED, FATAL")
    latency_ms: float = Field(..., description="Sub-atomic response latency")

class DiagnosticResponse(BaseModel):
    system_status: str = Field(..., description="Global holistic health marker indicating deployment readiness")
    engine_heartbeat: KernelVitals = Field(..., description="Core asynchronous event-loop vitality")
    graph_integrity: KernelVitals = Field(..., description="3.81M node structural stability matrix")
    neural_bridge: KernelVitals = Field(..., description="Gemini 1.5 Flash API synchronization cache status")
    resident_memory_mb: float = Field(..., description="Strict 150MB residency verification bound constraint")

