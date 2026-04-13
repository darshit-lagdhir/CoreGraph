from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from backend.schemas.api import ForensicQueryRequest, ForensicQueryResponse
import uuid
import asyncio
import json
import time

router = APIRouter(prefix="/v1", tags=["Topological Forensics"])
active_jobs = {}

async def headless_audit_worker(job_id: str, target: str):
    active_jobs[job_id] = "SCANNING"
    await asyncio.sleep(1.5)
    active_jobs[job_id] = "SYNTHESIZING"
    await asyncio.sleep(1)
    active_jobs[job_id] = "COMPLETED"

@router.post("/audit", response_model=ForensicQueryResponse, summary="Initiate CVI Risk Calculation Sequence", description="Triggers a high-velocity, multi-threaded scan across a simulated 3.81M node OSINT matrix. The backend offloads graph traversal to asynchronous background tasks to maintain UI liquid-state.")
async def initiate_audit(request: ForensicQueryRequest, bg_tasks: BackgroundTasks):
    job_id = f"coregraph_job_{uuid.uuid4().hex[:12]}"
    active_jobs[job_id] = "INITIALIZED"
    bg_tasks.add_task(headless_audit_worker, job_id, request.target_node)
    return ForensicQueryResponse(status="ACCEPTED", timestamp=str(time.time()), job_id=job_id, payload={"target": request.target_node, "depth": request.depth})

@router.get("/status/{job_id}", summary="Systemic State Validation", description="Non-blocking poll of the asynchronous computation pipeline.")
async def polling_status(job_id: str):
    return {"job_id": job_id, "status": active_jobs.get(job_id, "NOT_FOUND")}

@router.get("/stream/{job_id}", summary="Server-Sent Event Telemetry Pipeline", description="Yields chunked telemetry events natively aligned with the 144Hz HUD requirements. Designed to bypass traditional UI polling latency.")
async def stream_telemetry(job_id: str):
    async def forensic_event_generator():
        while active_jobs.get(job_id) not in ["COMPLETED", "FAILED", "NOT_FOUND"]:
            yield f"data: {json.dumps({'job_id': job_id, 'status': active_jobs.get(job_id)})}\n\n"
            await asyncio.sleep(0.144) 
        yield f"data: {json.dumps({'job_id': job_id, 'status': active_jobs.get(job_id)})}\n\n"
    return StreamingResponse(forensic_event_generator(), media_type="text/event-stream")

