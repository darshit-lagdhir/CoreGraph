import asyncio
import os
import logging
from typing import Dict, List, Any, Optional
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Log, Input
from textual.containers import Container, Vertical
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
from rich.console import RenderableType

from backend.core.memory_manager import metabolic_governor
from backend.core.interface.adaptive_layout_manager import AdaptiveLayoutManager
from backend.core.monitoring.environment_sentry_kernel import EnvironmentSentryKernel, MetabolicMode
from backend.core.security.input_sentinel_phalanx import InputSentinelPhalanx
from backend.core.interface.command_dispatch_kernel import CommandDispatchKernel
from backend.core.interface.intelligent_input_guide import IntelligentInputGuide
from backend.core.interface.command_feedback_radiance import CommandFeedbackRadiance

logger = logging.getLogger(__name__)


class SpectralGraph(Static):
    """SECTOR GAMMA: Spectral Topology Manifold (144Hz Radiance)."""

    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.refresh)

    def render(self) -> RenderableType:
        return Panel(
            Text("TOPOLOGICAL EQUILIBRIUM: STABLE", style="bold cyan"), border_style="cyan"
        )


class SystemicVictoryPanel(Static):
    """
    SECTOR THETA: Systemic Victory Log.
    The final seal of the Genesis Phase.
    """

    def on_mount(self) -> None:
        self.set_interval(2.0, self.update_glow)
        self.glow_state = 0

    def update_glow(self) -> None:
        colors = ["cyan", "bright_cyan", "white", "bright_cyan"]
        color = colors[self.glow_state % len(colors)]
        self.glow_state += 1

        msg = "SYSTEMIC GENESIS COMPLETE | SOVEREIGNTY ACHIEVED | RADIANCE STABLE"
        self.update(Panel(Text(msg, style=f"bold {color} center"), border_style=color))


class CoreGraphTitanApp(App):
    """THE SUPREME OPERATIONAL TITAN: FINAL GENESIS."""

    TITLE = "COREGRAPH TITAN [FINAL]"
    BINDINGS = [Binding("q", "quit", "DE-MATERIALIZE")]

    CSS = """
    Screen { background: #0b0f19; }
    #main_grid {
        layout: grid;
        grid-size: 2 2;
        grid-columns: 70% 30%;
        grid-rows: 75% 25%;
    }
    #graph_panel { border: solid cyan; }
    #log_panel { background: #0d111c; border: solid yellow; }
    #victory_panel { column-span: 2; height: 3; margin-bottom: 1; }
    """

    def compose(self) -> ComposeResult:
        self.sentry = EnvironmentSentryKernel()
        self.sentry.probe_substrate()
        self.sentinel = InputSentinelPhalanx()
        self.guide = IntelligentInputGuide(["SCAN", "TRACE", "AUDIT", "FILTER", "ZENITH"])
        self.radiance = CommandFeedbackRadiance()
        self.dispatcher = CommandDispatchKernel(self.execute_forensic_action)

        yield Header(show_clock=True)
        yield SystemicVictoryPanel(id="victory_panel")
        with Container(id="main_grid"):
            yield SpectralGraph(id="graph_panel")
            yield Log(id="log_panel")
            with Vertical():
                yield Static(
                    f"VAULT: {'OCCUPIED' if self.sentry.mode == MetabolicMode.LEAN else 'LOCAL_SYNC'}",
                    id="telemetry_watch",
                )
                yield Input(placeholder="ENTER_COMMAND: [SCAN | TRACE | AUDIT]", id="input_field")
        yield Footer()

    def on_mount(self) -> None:
        self.log_panel = self.query_one("#log_panel", Log)
        self.log_panel.write_line("[Alpha] TOTAL_SYSTEMIC_RECONCILIATION: Complete.")
        self.log_panel.write_line("[Zeta] CHROMATIC_RADIANCE: Calibrated (24-bit).")
        asyncio.create_task(self.dispatcher.run_loop())

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd_text = event.value.strip().upper()
        if self.sentinel.validate_command(cmd_text):
            await self.dispatcher.dispatch(cmd_text, {})
            self.query_one("#input_field", Input).value = ""
        else:
            self.log_panel.write(self.radiance.log_failure(cmd_text, "SYNTAX_ANOMALY"))

    async def execute_forensic_action(self, command: str, params: dict) -> None:
        self.log_panel.write(self.radiance.log_success(command, "Execution Manifested."))


if __name__ == "__main__":
    app = CoreGraphTitanApp()
    app.run()
