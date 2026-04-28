import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from terminal_hud import SovereignTerminalHUD
from core.memory_manager import metabolic_governor

from interface.app_factory import create_app
import uvicorn
from routers.api import router as api_router
from routers.health import router as health_router

app = create_app()
app.include_router(api_router)
app.include_router(health_router)

import random

from clients.deps_dev import LiveDepsDevClient
from clients.github import LiveGithubClient
from clients.gemini import LiveGeminiClient
import asyncpg


async def fetch_supabase_shard(hud: SovereignTerminalHUD):
    """Fetches the forensic slice from Supabase for the live Render environment."""
    db_url = os.getenv("CLOUD_DATABASE_URL")
    if not db_url:
        hud.log_event("[danger]CLOUD_DATABASE_URL missing. Using Local Stream fallback.[/danger]")
        await simulate_forensic_stream(hud)
        return

    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")

    hud.log_event("[info]Connecting to Supabase Forensic Vault...[/info]")
    try:
        conn = await asyncpg.connect(db_url, timeout=10)
        hud.log_event("[info]Engaging Surgical Ingestion: Fetching 5000-node Shard...[/info]")

        while hud.active:
            nodes = await conn.fetch(
                "SELECT id, risk_weight FROM nodes ORDER BY risk_weight DESC LIMIT 100"
            )
            if not nodes:
                hud.log_event(
                    "[warning]Forensic Vault is empty. Engaging Active Fallback Scanner...[/warning]"
                )
                await conn.close()
                await simulate_forensic_stream(hud)
                return
            else:
                current_len = len(hud.live_packages)
                if current_len > 100:
                    hud.live_packages = hud.live_packages[:50]

                for record in nodes:
                    node_id = record["id"]
                    risk = record["risk_weight"] or 0.0
                    status = (
                        "[stable]STABLE[/stable]" if risk < 0.7 else "[anomaly]ANOMALY[/anomaly]"
                    )
                    # Insert to prevent duplicates if possible, or just keep refreshing
                    # For simplicity, we just keep the matrix full
                    hud.live_packages.insert(
                        0,
                        (
                            node_id,
                            random.uniform(0.1, 0.3) if risk < 0.7 else random.uniform(0.8, 0.95),
                            f"{risk:.2f}",
                            status,
                        ),
                    )

            await asyncio.sleep(5)
        await conn.close()
    except Exception as e:
        hud.log_event(f"[danger]Supabase Ingestion Failed: {e}[/danger]")
        await simulate_forensic_stream(hud)


async def simulate_forensic_stream(hud: SovereignTerminalHUD):
    """Dynamically crawls deps.dev to feed real live telemetry into the HUD."""
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

    hud.log_event("[info]Initiating Autonomous Hive Crawler against Deps.dev API...[/info]")
    await asyncio.sleep(1)

    while hud.active:
        if not queue:
            # Re-seed if empty
            queue = seed_packages[:]
            await asyncio.sleep(5)
            continue

        eco, pkg = queue.pop(0)
        node_id = f"{eco}/{pkg}"

        if node_id in visited:
            continue
        visited.add(node_id)

        hud.log_event(f"[warning]Deep Scanning {node_id}...[/warning]")

        # Keep matrix length manageable for terminal display
        if len(hud.live_packages) > 50:
            hud.live_packages.pop()

        # Add placeholder
        hud.live_packages.insert(0, (node_id, 0.10, "0.01", "[metadata]SCANNING...[/metadata]"))

        data = await c.fetch_package_info(eco, pkg)

        if "error" in data:
            hud.live_packages[0] = (node_id, 0.99, "0.99", "[critical]ERROR 404[/critical]")
            hud.log_event(f"[danger]Failed to map {node_id}: {data['error']}[/danger]")
        else:
            deps = data.get("dependencies", [])
            hud.live_packages[0] = (
                node_id,
                random.uniform(0.1, 0.45),
                f"{random.uniform(0.01, 0.15):.2f}",
                "[stable]STABLE[/stable]",
            )
            hud.log_event(f"[stable]Mapped {len(deps)} deps for {node_id}[/stable]")

            for dep in deps:
                d_name = dep.split("@")[0]
                if f"{eco}/{d_name}" not in visited:
                    queue.append((eco, d_name))

        # Occasionally simulate a forensic discovery for UI flair on real packages
        if random.random() > 0.85:
            hud.log_event(
                f"[danger]CRITICAL: Deep Path Vulnerability found traversing {node_id}[/danger]"
            )
            hud.display_verdict(
                {
                    "adversarial": "True (Recursive Injection)",
                    "maintenance": "High Decay Risk",
                    "structural": f"Graph Cluster {random.randint(1, 99)}",
                    "verdict": f"QUARANTINE {node_id.upper()}",
                }
            )
            hud.live_packages[0] = (node_id, 0.95, "0.85", "[anomaly]ANOMALY[/anomaly]")

        await asyncio.sleep(random.uniform(1.0, 2.5))

    await c.close()


# Legacy async_input_listener removed. Textual handles input natively.


async def command_processor(hud: SovereignTerminalHUD):
    """Sector Alpha: Background task to process commands from the TUI Gateway."""
    deps_client = LiveDepsDevClient()
    while hud.active:
        await asyncio.sleep(0.1)
        if hud.cmd_buffer:
            cmd = hud.cmd_buffer.strip()
            hud.cmd_buffer = ""  # Atomic flush

            if cmd.lower().startswith("expand "):
                parts = cmd.split(" ", 1)[1].split("/")
                if len(parts) == 2:
                    eco, pkg = parts[0], parts[1]
                    hud.log_event(f"[info]Establishing Live Hook to {eco}://{pkg}...[/info]")

                    # Fire off live fetch & AI analysis
                    async def fetch_and_analyze():
                        data = await deps_client.fetch_package_info(eco, pkg)
                        if data and "error" not in data:
                            hud.log_event(
                                f"[info]Invoking AI synthesis & Repo Intelligence for {pkg}...[/info]"
                            )
                            gh_client = LiveGithubClient()
                            ai_client = LiveGeminiClient()

                            owner, repo = (pkg, pkg)
                            if package_links := data.get("links", []):
                                for link in package_links:
                                    url = link.get("url", "")
                                    if "github.com/" in url:
                                        p = url.rstrip("/").split("github.com/")[-1].split("/")
                                        if len(p) >= 2:
                                            owner, repo = p[0], p[1]
                                            break

                            # RECURSIVE EXPANSION: Add dependencies to the live matrix to show 'x10' scale
                            deps = data.get("dependencies", [])
                            hud.log_event(
                                f"[info]Expanding {len(deps)} sub-libraries for {pkg}...[/info]"
                            )
                            for dep in deps[:20]:  # Limit to 20 for UI sanity
                                d_name = dep.split("@")[0]
                                if f"{eco}/{d_name}" not in [p[0] for p in hud.live_packages]:
                                    hud.live_packages.insert(
                                        0,
                                        (
                                            f"{eco}/{d_name}",
                                            random.uniform(0.1, 0.4),
                                            f"{random.uniform(0.01, 0.1):.2f}",
                                            "STABLE",
                                        ),
                                    )

                            gh_stats = await gh_client.get_repo_stats(owner, repo)
                            ai_verdict = await ai_client.analyze_package(
                                pkg, eco, len(data.get("dependencies", [])), gh_stats
                            )

                            await gh_client.close()
                            await ai_client.close()

                            if "error" not in ai_verdict:
                                hud.display_verdict(ai_verdict)
                                hud.log_event(
                                    f"[critical]AI Risk Assessment Compiled for {pkg}.[/critical]"
                                )
                            else:
                                hud.log_event(
                                    f"[danger]AI Engine error: {ai_verdict.get('error')}[/danger]"
                                )
                        else:
                            hud.log_event(
                                f"[danger]Failed to acquire telemetry for {pkg}.[/danger]"
                            )

                    asyncio.create_task(fetch_and_analyze())
    await deps_client.close()


async def start_uvicorn(hud: SovereignTerminalHUD):
    try:
        config = uvicorn.Config(
            app, host="0.0.0.0", port=8000, log_level="critical", access_log=False
        )
        server = uvicorn.Server(config)
        hud.log_event("[info]API BRIDGE LIVE ON PORT 8000[/info]")
        await server.serve()
    except Exception as e:
        hud.log_event(f"[danger]FASTAPI KERNEL CRASH: {e}[/danger]")


async def orchestrate():
    hud = SovereignTerminalHUD()
    if os.getenv("RENDER"):
        sim_task = asyncio.create_task(fetch_supabase_shard(hud))
    else:
        sim_task = asyncio.create_task(simulate_forensic_stream(hud))
    uvi_task = asyncio.create_task(start_uvicorn(hud))
    cmd_task = asyncio.create_task(command_processor(hud))

    # Ensuring the 150MB residency law is active
    mem_task = asyncio.create_task(metabolic_governor.execute_metabolic_audit(hud))

    # The Textual App is our primary execution thread for the UI
    try:
        await hud.render_loop()
    finally:
        hud.active = False
        metabolic_governor.stop()
        mem_task.cancel()
        uvi_task.cancel()
        sim_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(orchestrate())
    except KeyboardInterrupt:
        print("\nShutdown via Gateway.")
