import asyncio
import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from terminal_hud import SovereignTerminalHUD
from core.memory_manager import limiter_kernel

from interface.app_factory import create_app
import uvicorn
from routers.api import router as api_router
from routers.health import router as health_router

app = create_app()
app.include_router(api_router)
app.include_router(health_router)

import random

async def simulate_forensic_stream(hud: SovereignTerminalHUD):
    """Dynamically feeds telemetry so the HUD isn't static."""
    packages = ["npm/react", "pypi/requests", "npm/express", "crates/serde", "npm/malicious-pkg", "pypi/Django"]
    states = ["[stable]STABLE[/stable]", "[anomaly]ANOMALY[/anomaly]", "[critical]CRITICAL[/critical]", "[metadata]METADATA[/metadata]"]
    
    # Send a couple initial log bursts
    await asyncio.sleep(1)
    hud.log_event("[info]3.81M Node Ingestion Initialized...[/info]")
    await asyncio.sleep(1)
    hud.log_event("[warning]Hadronic Centality Mapping Started...[/warning]")

    while hud.active:
        await asyncio.sleep(random.uniform(0.5, 2.5))
        
        # Inject random forensic discoveries into the log
        target = random.choice(packages)
        if random.random() > 0.7:
            hud.log_event(f"[danger]CRITICAL: Deep Path Vulnerability found in {target}[/danger]")
            
        if random.random() > 0.8:
            hud.display_verdict({
                "adversarial": "True (Supply Chain Inject)",
                "maintenance": "High Decay Risk",
                "structural": "Graph Shard 44B",
                "verdict": f"QUARANTINE {target.upper()}"
            })
        else:
            hud.display_verdict({
                "adversarial": "False",
                "maintenance": "Stable",
                "structural": "Graph Shard 12A",
                "verdict": "VERIFIED CLEAN"
            })

async def async_input_listener(hud: SovereignTerminalHUD):
    while hud.active:
        hud.cmd_status = "[stable]AWAITING DIRECTIVE (BACKGROUND)[/stable]"
        await asyncio.sleep(1)

async def start_uvicorn(hud: SovereignTerminalHUD):
    try:
        config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="critical", access_log=False)
        server = uvicorn.Server(config)
        hud.log_event("[info]API BRIDGE LIVE ON PORT 8000[/info]")
        await server.serve()
    except Exception as e:
        hud.log_event(f"[danger]FASTAPI KERNEL CRASH: {e}[/danger]")

async def orchestrate():
    hud = SovereignTerminalHUD()
    hud_task = asyncio.create_task(hud.stream_hud())
    sim_task = asyncio.create_task(simulate_forensic_stream(hud))
    input_task = asyncio.create_task(async_input_listener(hud))
    uvi_task = asyncio.create_task(start_uvicorn(hud))
    mem_task = asyncio.create_task(limiter_kernel.enforce_residency(hud))

    while hud.active:
        await asyncio.sleep(0.5)

    limiter_kernel.active = False
    mem_task.cancel()
    uvi_task.cancel()
    sim_task.cancel()
    input_task.cancel()
    hud_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(orchestrate())
    except KeyboardInterrupt:
        print("\nShutdown via Gateway.")

