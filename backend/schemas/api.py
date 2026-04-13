from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any

class ForensicQueryRequest(BaseModel):
    target_node: str = Field(..., max_length=255, description="Exact package identifier or topological entity name targeted for isolation.")
    depth: int = Field(default=1, ge=1, le=5, description="Hadronic scan depth. Limits the radial propagation for the dependency matrix bounding.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target_node": "react-dom",
                "depth": 3
            }
        }
    )

class ForensicQueryResponse(BaseModel):
    status: str = Field(..., description="Job lifecycle status. Tracks the async transition mathematically (ACCEPTED, SCANNING, SYNTHESIZING).")
    timestamp: str = Field(..., description="Epoch UTC of ingestion. Acts as the zero-point for latency drift verification.")
    job_id: str = Field(..., description="Globally unique task tracking hash. The cryptographic identity of the analysis pipeline.")
    payload: Optional[Dict[str, Any]] = Field(None, description="Pre-calculated CVI bounds and partial topological tensors.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ACCEPTED",
                "timestamp": "1712959241.123",
                "job_id": "coregraph_job_8f7b2c019a3b",
                "payload": {
                    "estimated_nodes": 3810000,
                    "cvi_score": 0.94
                }
            }
        }
    )

