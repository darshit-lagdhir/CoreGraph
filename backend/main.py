import asyncio
import sys
import os
import logging
import random
import asyncpg
import json

# Sector Alpha: Path Alignment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from terminal_hud import SovereignTerminalHUD
from core.memory_manager import metabolic_governor
from core.monitoring.environment_sentry_kernel import EnvironmentSentryKernel, MetabolicMode
from core.ingestion.data_ingestion_multiplexer import DataIngestionMultiplexer

from clients.deps_dev import LiveDepsDevClient
from clients.github import LiveGithubClient
from clients.gemini import LiveGeminiClient

# Sector Beta: App Logic Bridge
from interface.app_factory import create_app
import uvicorn
from routers.api import router as api_router
from routers.health import router as health_router

app = create_app()
app.include_router(api_router)
app.include_router(health_router)

logger = logging.getLogger(__name__)


async def fetch_supabase_shard(hud: SovereignTerminalHUD):
    """
    SECTOR GAMMA: Supabase Shard Ingestion.
    Fetches the 5000-node forensic slice for the cloud preview.
    """
    db_url = os.getenv("CLOUD_DATABASE_URL")
    if not db_url:
        hud.log_event("[danger]CLOUD_DATABASE_URL missing. Using fallback telemetry.[/danger]")
        await generate_fallback_data(hud)
        return

    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")

    hud.log_event("[info]Connecting to Supabase Forensic Vault...[/info]")
    try:
        # Sector Gamma: Secure Connection Handshake
        conn = await asyncpg.connect(db_url, timeout=10)
        hud.log_event("[info]Engaging Surgical Ingestion: Fetching 5000-node Shard...[/info]")

        # Sector Gamma: Rapid Shard Retrieval
        nodes = await conn.fetch(
            "SELECT id, risk_weight FROM nodes ORDER BY risk_weight DESC LIMIT 100"
        )

        if not nodes:
            hud.log_event("[warning]Forensic Vault is empty. Generating seed data...[/warning]")
            await generate_fallback_data(hud)
        else:
            for record in nodes:
                node_id = record["id"]
                risk = record["risk_weight"] or 0.0
                status = "STABLE" if risk < 0.7 else "ANOMALY"

                hud.live_packages.append(
                    (
                        node_id,
                        (
                            random.uniform(0.1, 0.3)
                            if status == "STABLE"
                            else random.uniform(0.8, 0.95)
                        ),
                        f"{risk:.2f}",
                        status,
                    )
                )
            hud.log_event(
                f"[stable]Sovereign Shard Manifested: {len(nodes)} nodes ingested.[/stable]"
            )

        await conn.close()
    except Exception as e:
        hud.log_event(f"[danger]Supabase Ingestion Failed: {e}[/danger]")
        hud.log_event("[info]Switching to Local Fallback Metabolism...[/info]")
        await generate_fallback_data(hud)


async def generate_fallback_data(hud: SovereignTerminalHUD):
    """Sector Omega: Fallback data to prevent black-screen vacuum."""
    fallbacks = [
        ("npm/react", 0.11, "0.02", "STABLE"),
        ("pypi/requests", 0.15, "0.04", "STABLE"),
        ("crates/serde", 0.12, "0.01", "STABLE"),
        ("npm/lodash", 0.95, "0.85", "ANOMALY"),
        ("pypi/django", 0.22, "0.05", "STABLE"),
    ]
    for pkg, ent, risk, status in fallbacks:
        hud.live_packages.append((pkg, ent, risk, status))


async def simulate_forensic_stream(hud: SovereignTerminalHUD):
    """
    SECTOR ALPHA: Live Ingestion Stream (Local/Beast Mode).
    """
    seed_packages = [
        ("npm", "react"),
        ("pypi", "requests"),
        ("crates", "serde"),
        ("npm", "lodash"),
        ("pypi", "django"),
    ]
    c = LiveDepsDevClient()
    visited = set()
    queue = seed_packages[:]

    hud.log_event("[info]Initiating Local Hadronic Stream...[/info]")

    while hud.active:
        try:
            if not queue:
                queue = seed_packages[:]
                await asyncio.sleep(5)
                continue

            eco, pkg = queue.pop(0)
            node_id = f"{eco}/{pkg}"
            if node_id in visited:
                continue
            visited.add(node_id)

            if len(hud.live_packages) > 50:
                hud.live_packages.pop()

            data = await c.fetch_package_info(eco, pkg)
            if "error" not in data:
                hud.live_packages.insert(
                    0,
                    (
                        node_id,
                        random.uniform(0.1, 0.45),
                        f"{random.uniform(0.01, 0.15):.2f}",
                        "STABLE",
                    ),
                )
                hud.log_event(
                    f"[stable]Mapped {len(data.get('dependencies', []))} deps for {node_id}[/stable]"
                )

                for dep in data.get("dependencies", [])[:3]:
                    d_name = dep.split("@")[0]
                    if f"{eco}/{d_name}" not in visited:
                        queue.append((eco, d_name))
        except Exception as e:
            hud.log_event(f"[danger]Stream Drift: {e}[/danger]")

        await asyncio.sleep(random.uniform(1.0, 3.0))
    await c.close()


async def command_processor(hud: SovereignTerminalHUD):
    """Processes commands from the TUI Gateway."""
    while hud.active:
        await asyncio.sleep(0.1)
        if hud.cmd_buffer:
            cmd = hud.cmd_buffer.strip()
            hud.cmd_buffer = ""
            # Command logic...


async def start_uvicorn(hud: SovereignTerminalHUD):
    try:
        # Use 0.0.0.0 for Render compliance
        config = uvicorn.Config(
            app, host="0.0.0.0", port=8000, log_level="critical", access_log=False
        )
        server = uvicorn.Server(config)
        hud.log_event("[info]API BRIDGE LIVE ON PORT 8000[/info]")
        await server.serve()
    except Exception as e:
        hud.log_event(f"[danger]FASTAPI KERNEL CRASH: {e}[/danger]")


async def orchestrate():
    """
    THE MASTER ORCHESTRATOR: RECONCILED GENESIS.
    """
    hud = SovereignTerminalHUD()
    sentry = EnvironmentSentryKernel()
    sentry.probe_substrate()

    multiplexer = DataIngestionMultiplexer(sentry.mode)
    await multiplexer.initialize_conduit()

    hud.log_event(f"[info]ENVIRONMENT_SENTRY: {sentry.mode.name} DETECTED.[/info]")

    # Bifurcated Data Path
    if sentry.mode == MetabolicMode.LEAN or os.getenv("RENDER"):
        data_task = asyncio.create_task(fetch_supabase_shard(hud))
    else:
        data_task = asyncio.create_task(simulate_forensic_stream(hud))

    # Support Tasks
    mem_task = asyncio.create_task(metabolic_governor.execute_metabolic_audit(hud))
    uvi_task = asyncio.create_task(start_uvicorn(hud))
    cmd_task = asyncio.create_task(command_processor(hud))

    try:
        await hud.render_loop()
    finally:
        hud.active = False
        metabolic_governor.stop()
        mem_task.cancel()
        data_task.cancel()
        uvi_task.cancel()
        cmd_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(orchestrate())
    except KeyboardInterrupt:
        print("\nShutdown via Gateway.")
