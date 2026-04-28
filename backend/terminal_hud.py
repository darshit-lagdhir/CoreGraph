import asyncio
import random
import time
import psutil
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Static,
    DataTable,
    Log,
    Input,
    Sparkline,
    TabbedContent,
    TabPane,
)
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel

from backend.core.memory_manager import metabolic_governor

# =========================================================================================
# COREGRAPH TITAN HUD V4: ZERO-DEPENDENCY GENESIS (DEPLOYMENT READY)
# =========================================================================================


class MatrixTable(DataTable):
    """Sector Beta: The Central Hadronic Audit Matrix."""

    pass


class SovereignImpact(Static):
    """Sector Delta: Sovereign Impact Report Widget."""

    def update_verdict(self, data: dict):
        lines = [
            f"[bold cyan]ADVERSARIAL:[/bold cyan] {data.get('adversarial', 'False')}",
            f"[bold cyan]MAINTENANCE:[/bold cyan] {data.get('maintenance', 'Low')}",
            f"[bold cyan]STRUCTURAL:[/bold cyan] {data.get('structural', 'Stable')}",
            "",
            f"[bold reverse red] FINAL VERDICT: {data.get('verdict', 'UNKNOWN')} [/bold reverse red]",
        ]
        self.update(
            Panel(
                "\n".join(lines),
                title="[bold magenta]Sovereign Impact Report[/bold magenta]",
                border_style="red",
            )
        )


class CoreGraphTitanApp(App):
    """
    The Supreme Terminal Application.
    Sector Alpha: High-Velocity Forensic Visualization.
    """

    TITLE = "CoreGraphTitanApp"
    SUB_TITLE = "SYSTEM_PULSE: STARTING..."

    CSS = """
    Screen { background: #0b0f19; }
    #main_container { layout: horizontal; padding: 1; }
    #left_panel { width: 60%; border: solid cyan; background: #0d111c; }
    #right_panel { width: 40%; layout: vertical; margin-left: 1; }
    #log_panel { height: 60%; border: solid yellow; background: #0d111c; }
    #verdict_panel { height: 40%; border: solid red; margin-top: 1; background: #0d111c; }
    #input_container { height: 3; dock: bottom; background: #1a1e2a; border-top: double cyan; padding: 0 1; }
    DataTable { height: 1fr; background: #0d111c; color: #ddd; }
    DataTable > .datatable--header { background: #1a1e2a; color: cyan; text-style: bold; }
    Log { background: #0d111c; color: #888; }
    """

    BINDINGS = [
        Binding("q", "quit", "Shutdown Gateway"),
        Binding("c", "clear_log", "Clear Forensic Log"),
    ]

    def __init__(self, legacy_hud=None):
        super().__init__()
        self.legacy_hud = legacy_hud
        self.last_matrix_data = None
        self.cpu_usage = 0.0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_container"):
            with Vertical(id="left_panel"):
                yield Static(" [bold cyan]CENTRAL HADRONIC AUDIT MATRIX[/bold cyan]")
                yield MatrixTable(id="matrix_view")
            with Vertical(id="right_panel"):
                with TabbedContent():
                    with TabPane("Forensic Log"):
                        yield Log(id="log_panel")
                    with TabPane("System Health"):
                        yield Static(" [bold yellow]METABOLIC OSCILLOSCOPE[/bold yellow]")
                        self.spark = Sparkline([random.random() for _ in range(20)])
                        yield self.spark
                    with TabPane("Node Intelligence"):
                        self.detail = Static(
                            Panel("Select node for intelligence", border_style="cyan")
                        )
                        yield self.detail
                yield SovereignImpact(id="verdict_panel")

        with Horizontal(id="input_container"):
            yield Static("> ", id="prompt")
            yield Input(placeholder="COMMAND_PHALANX: [EXPAND | CLEAR | FILTER]", id="input_field")
        yield Footer()

    def on_mount(self) -> None:
        self.matrix = self.query_one("#matrix_view", MatrixTable)
        self.log_panel = self.query_one("#log_panel", Log)
        self.impact = self.query_one("#verdict_panel", SovereignImpact)
        self.cmd_input = self.query_one("#input_field", Input)

        self.matrix.add_columns("NODE ID", "ENTROPY", "RISK", "SOVEREIGN STATUS")
        self.matrix.cursor_type = "row"
        self.matrix.focus()

        self.set_interval(0.2, self.refresh_system_telemetry)
        psutil.cpu_percent(interval=None)

        self.log_panel.write_line("[bold green]CoreGraph Titan App Online.[/bold green]")

        if self.legacy_hud and self.legacy_hud.verdict:
            self.impact.update_verdict(self.legacy_hud.verdict)

    def refresh_system_telemetry(self) -> None:
        try:
            metabolic_governor.audit_heartbeat()
            rss = metabolic_governor.get_physical_rss_us()
            self.cpu_usage = psutil.cpu_percent(interval=None)

            node_count = len(self.legacy_hud.live_packages) if self.legacy_hud else 0
            self.sub_title = f"NODES: {node_count} | RSS: {rss:.1f}MB | CPU: {self.cpu_usage:.1f}%"

            if self.legacy_hud:
                query = self.legacy_hud.search_query.lower()
                current_data = list(self.legacy_hud.live_packages)

                if query:
                    current_data = [p for p in current_data if query in str(p[0]).lower()]

                if current_data != self.last_matrix_data:
                    cursor_row = self.matrix.cursor_row
                    self.matrix.clear()
                    for pkg, ent, risk, status in current_data[:40]:
                        ent_color = "red" if ent > 0.8 else ("yellow" if ent > 0.4 else "green")
                        s_styled = (
                            f"[bold green]STABLE[/bold green]"
                            if "STABLE" in str(status).upper()
                            else f"[bold red]{status}[/bold red]"
                        )
                        self.matrix.add_row(
                            f"[bold cyan]{pkg}[/bold cyan]",
                            f"[{ent_color}]{ent:.2f}[/{ent_color}]",
                            f"[bold]{risk}[/bold]",
                            s_styled,
                        )

                    if cursor_row < len(current_data):
                        self.matrix.move_cursor(row=cursor_row)
                    self.last_matrix_data = current_data

                if self.legacy_hud.verdict:
                    self.impact.update_verdict(self.legacy_hud.verdict)
        except Exception:
            pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_data = self.matrix.get_row(event.row_key)
        pkg_name = (
            str(row_data[0]).split("]")[1].split("[")[0]
            if "]" in str(row_data[0])
            else str(row_data[0])
        )
        intel = [
            f"[bold cyan]NODE:[/bold cyan] {pkg_name}",
            f"[bold yellow]ENTROPY:[/bold yellow] {row_data[1]}",
            f"[bold red]RISK VECTOR:[/bold red] {row_data[2]}",
            f"[bold green]STATUS:[/bold green] {row_data[3]}",
        ]
        self.detail.update(Panel("\n".join(intel), border_style="cyan"))
        if self.legacy_hud:
            self.legacy_hud.process_command(f"expand {pkg_name}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if self.legacy_hud:
            self.legacy_hud.process_command(cmd)
            self.log_panel.write_line(f"[bold yellow]> {cmd}[/bold yellow]")
        self.cmd_input.value = ""


class SovereignTerminalHUD:
    def __init__(self):
        self.active = True
        self.live_packages = []
        self.cmd_buffer = ""
        self.search_query = ""
        self.verdict = None
        self.app = CoreGraphTitanApp(legacy_hud=self)

    def process_command(self, cmd: str):
        cmd_lower = cmd.lower()
        if cmd_lower.startswith("expand "):
            self.cmd_buffer = cmd
        else:
            self.search_query = cmd_lower

    def log_event(self, msg: str):
        try:
            if self.app.log_panel:
                self.app.log_panel.write_line(msg)
        except Exception:
            pass

    def display_verdict(self, data: dict):
        self.verdict = data

    async def render_loop(self):
        await self.app.run_async()


if __name__ == "__main__":
    hud = SovereignTerminalHUD()
    asyncio.run(hud.render_loop())
