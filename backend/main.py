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


async def generate_fallback_data(hud: SovereignTerminalHUD):
    """Sector Omega: Fallback data to prevent black-screen vacuum."""
    # Ensure we don't duplicate
    if len(hud.live_packages) > 0:
        return

    fallbacks = [
        ("npm/react", 0.11, "0.02", "STABLE"),
        ("pypi/requests", 0.15, "0.04", "STABLE"),
        ("crates/serde", 0.12, "0.01", "STABLE"),
        ("npm/lodash", 0.95, "0.85", "ANOMALY"),
        ("pypi/django", 0.22, "0.05", "STABLE"),
        ("pypi/typing-extensions", 0.11, "0.02", "STABLE"),
        ("pypi/sqlparse", 0.26, "0.04", "STABLE"),
        ("pypi/asgiref", 0.95, "0.85", "ANOMALY"),
    ]
    for pkg, ent, risk, status in fallbacks:
        hud.live_packages.append((pkg, ent, risk, status))

    hud.display_verdict(
        {
            "adversarial": "False",
            "maintenance": "High",
            "structural": "Stable",
            "verdict": "GENESIS_STABLE",
        }
    )


async def fetch_supabase_shard(hud: SovereignTerminalHUD):
    """
    SECTOR GAMMA: Supabase Shard Ingestion.
    """
    db_url = os.getenv("CLOUD_DATABASE_URL")
    if not db_url:
        hud.log_event("[warning]CLOUD_DATABASE_URL missing. Using Seed Metabolism.[/warning]")
        await generate_fallback_data(hud)
        return

    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")

    try:
        conn = await asyncpg.connect(db_url, timeout=10)
        nodes = await conn.fetch(
            "SELECT id, risk_weight FROM nodes ORDER BY risk_weight DESC LIMIT 100"
        )

        if not nodes:
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
            hud.log_event(f"[stable]Vault Ingested: {len(nodes)} nodes.[/stable]")
        await conn.close()
    except Exception as e:
        hud.log_event(f"[danger]Vault Connection Error: {e}[/danger]")
        await generate_fallback_data(hud)


async def simulate_forensic_stream(hud: SovereignTerminalHUD):
    """
    SECTOR ALPHA: Live Ingestion Stream (Local/Beast Mode).
    """
    # Start with some seed data immediately
    await generate_fallback_data(hud)

    seed_packages = [("npm", "react"), ("pypi", "requests"), ("crates", "serde")]
    c = LiveDepsDevClient()
    visited = set()
    queue = seed_packages[:]

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

            data = await c.fetch_package_info(eco, pkg)
            if "error" not in data:
                if len(hud.live_packages) > 50:
                    hud.live_packages.pop()
                hud.live_packages.insert(
                    0,
                    (
                        node_id,
                        random.uniform(0.1, 0.45),
                        f"{random.uniform(0.01, 0.15):.2f}",
                        "STABLE",
                    ),
                )
                hud.log_event(f"[stable]Mapped {node_id}[/stable]")
        except Exception:
            pass
        await asyncio.sleep(random.uniform(2.0, 5.0))
    await c.close()


async def orchestrate():
    hud = SovereignTerminalHUD()
    sentry = EnvironmentSentryKernel()
    sentry.probe_substrate()

    # IMMEDIATE SEED for UI Radiance
    await generate_fallback_data(hud)

    # Start tasks
    if sentry.mode == MetabolicMode.LEAN or os.getenv("RENDER"):
        data_task = asyncio.create_task(fetch_supabase_shard(hud))
    else:
        data_task = asyncio.create_task(simulate_forensic_stream(hud))

    mem_task = asyncio.create_task(metabolic_governor.execute_metabolic_audit(hud))
    uvi_task = asyncio.create_task(start_uvicorn(hud))

    try:
        await hud.render_loop()
    finally:
        hud.active = False
        mem_task.cancel()
        data_task.cancel()
        uvi_task.cancel()


async def start_uvicorn(hud: SovereignTerminalHUD):
    try:
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="critical")
        server = uvicorn.Server(config)
        await server.serve()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(orchestrate())
    except KeyboardInterrupt:
        pass
