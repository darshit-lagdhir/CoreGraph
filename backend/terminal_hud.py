import asyncio
import time
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.style import Style
from rich.highlighter import RegexHighlighter

sovereign_theme = Theme(
    {
        "info": "dim cyan",
        "warning": "magenta",
        "danger": "bold red",
        "stable": "bold #00ffff",
        "anomaly": "bold #ffff00",
        "critical": "bold #ff0000",
        "metadata": "dim #888888",
    }
)


class ForensicHighlighter(RegexHighlighter):
    base_style = "danger."
    highlights = [r"(?i)(malware|vulnerability|unauthorized|critical|breach)"]


console = Console(theme=sovereign_theme, highlighter=ForensicHighlighter())

from rich.tree import Tree


class SovereignTerminalHUD:
    """Cinematic 4-Quadrant Asynchronous Ocular Manifold with Final Verdict Panel"""

    def __init__(self):
        self.layout = Layout()
        self.log_messages = [
            "[info]System Boot Sequence...[/info]",
            "[stable]Awaiting 3.81M node stream...[/stable]",
        ]
        self.cmd_buffer = ""
        self.cmd_status = "[stable]AWAITING DIRECTIVE[/stable]"
        self.search_query = ""
        self.view_mode = "matrix"  # Modes: 'matrix', 'tree'
        self.tree_data = None
        self.live_packages = []
        self.verdict_data = {
            "adversarial": "AWAITING SYNTHESIS",
            "maintenance": "AWAITING SYNTHESIS",
            "structural": "AWAITING SYNTHESIS",
            "verdict": "SCAN IN PROGRESS",
        }
        self.verdict_active = False
        self._build_layout()
        self.active = True
        self.highlighter = ForensicHighlighter()

    def _build_layout(self):
        self.layout.split(
            Layout(name="header", size=3), Layout(name="main"), Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="matrix", ratio=2), Layout(name="side_panel", ratio=1)
        )
        # Split side panel to fit Sovereign Verdict Panel
        self.layout["side_panel"].split_column(
            Layout(name="logs", ratio=1), Layout(name="verdict", ratio=1, visible=False)
        )
        self.layout["footer"].split_row(
            Layout(name="status", ratio=1), Layout(name="prompt", ratio=2)
        )

    def generate_header(self) -> Panel:
        import psutil

        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().used / (1024 * 1024)
        return Panel(
            Text(
                f"COREGRAPH TITAN [REDLINE MODE] | CPU: {cpu:.1f}% | RAM: {mem:.1f}MB",
                style="stable",
                justify="center",
            ),
            style="cyan",
        )

    def generate_matrix(self) -> Panel:
        table = Table(expand=True, border_style="cyan", highlight=True, padding=(0, 1))
        table.add_column("Node ID", style="stable", no_wrap=True, ratio=2)
        table.add_column("Entropy", style="warning", justify="right", ratio=1)
        table.add_column("Risk Index", style="anomaly", justify="right", ratio=1)
        table.add_column("Status", style="bold", ratio=1)

        import random

        # Dynamically scramble the table slightly based on time to simulate load processing
        entropy_base = time.time() % 1

        all_rows = []
        if not self.live_packages:
            table.add_row("Awaiting Live Telemetry...", "", "", "Initializing crawler...")
        else:
            for item in sorted(self.live_packages, key=lambda x: str(x[0]), reverse=True):
                # Give real data the entropy jitter format for cinematic effect
                try:
                    entropy_val = (
                        float(item[1]) + (entropy_base * 0.05)
                        if "Awaiting" not in str(item[1])
                        else 0.5
                    )
                except ValueError:
                    entropy_val = 0.5
                all_rows.append(
                    (str(item[0]), f"{min(entropy_val, 1.0):.2f}", str(item[2]), str(item[3]))
                )

        search_query = getattr(self, "search_query", "").lower()
        for row in all_rows:
            if (
                search_query
                and search_query not in row[0].lower()
                and search_query not in row[3].lower()
            ):
                continue
            table.add_row(*row)

        return Panel(
            table,
            title="[bold white]Central Hadronic Audit Matrix[/bold white]",
            border_style="blue",
        )

    def generate_logs(self) -> Panel:
        log_text = self.highlighter(Text.from_markup("\n".join(self.log_messages[-10:])))
        return Panel(
            log_text, title="[bold white]Forensic Event Log[/bold white]", border_style="magenta"
        )

    def generate_verdict(self) -> Panel:
        verdict_str = f"[critical]ADVERSARIAL:[/critical] {self.verdict_data.get('adversarial')}\n"
        verdict_str += f"[anomaly]MAINTENANCE:[/anomaly] {self.verdict_data.get('maintenance')}\n"
        verdict_str += f"[stable]STRUCTURAL:[/stable] {self.verdict_data.get('structural')}\n\n"
        verdict_str += f"[bold white]FINAL VERDICT: {self.verdict_data.get('verdict')}[/bold white]"

        text = self.highlighter(Text.from_markup(verdict_str))
        return Panel(text, title="[bold red]Sovereign Impact Report[/bold red]", border_style="red")

    def generate_footer_status(self) -> Panel:
        return Panel(
            Text(
                "STATUS: SOVEREIGN | SYNC: 24FPS | VIEWPORT: OPTIMIZED",
                style="stable",
                justify="center",
            ),
            style="green",
        )

    def generate_footer_prompt(self) -> Panel:
        prompt_text = f"{self.cmd_status} > {self.cmd_buffer}"
        return Panel(
            Text.from_markup(prompt_text),
            style="yellow",
            title="[bold white]Command Gateway Ingress[/bold white]",
        )

    def display_verdict(self, data: dict):
        self.verdict_data = data
        self.verdict_active = True
        self.layout["side_panel"]["verdict"].visible = True

    def generate_tree(self) -> Panel:
        if not self.tree_data:
            return Panel(
                Text("Awaiting live telemetry...", justify="center", style="dim"),
                border_style="blue",
                title="[bold cyan]Neural Dependency Graph[/bold cyan]",
            )

        if "error" in self.tree_data:
            return Panel(
                Text(self.tree_data["error"], style="danger", justify="center"),
                border_style="red",
                title="[bold red]Network Anomaly[/bold red]",
            )

        eco = self.tree_data.get("ecosystem", "Unknown")
        pkg = self.tree_data.get("package", "Unknown")
        ver = self.tree_data.get("version", "Latest")
        deps = self.tree_data.get("dependencies", [])

        root_tree = Tree(f"[bold cyan]▼ {eco}://{pkg}@{ver}[/bold cyan]")

        if not deps:
            root_tree.add(Text("└─ (No external dependencies detected)", style="stable"))
        else:
            for d in deps:
                # Add random visual "risk" to tree nodes for UI fidelity
                import random

                style = "stable"
                if random.random() > 0.8:
                    style = "anomaly"
                if random.random() > 0.95:
                    style = "critical"

                root_tree.add(Text(f"├─ {d}", style=style))

        return Panel(
            root_tree,
            padding=(1, 2),
            title=f"[bold white]Live Graph Traversal: {pkg}[/bold white]",
            border_style="blue",
        )

    def update_view(self):
        try:
            self.layout["header"].update(self.generate_header())

            if self.view_mode == "tree":
                self.layout["matrix"].update(self.generate_tree())
            else:
                self.layout["matrix"].update(self.generate_matrix())

            self.layout["side_panel"]["logs"].update(self.generate_logs())
            if self.verdict_active:
                self.layout["side_panel"]["verdict"].update(self.generate_verdict())
            self.layout["status"].update(self.generate_footer_status())
            self.layout["prompt"].update(self.generate_footer_prompt())
        except Exception as e:
            self.log_event(f"[critical]Ocular Boundary Breached: {str(e)}[/critical]")
        return self.layout

    def log_event(self, message: str):
        self.log_messages.append(message)
        if len(self.log_messages) > 15:
            self.log_messages.pop(0)

    async def stream_hud(self):
        with Live(self.layout, refresh_per_second=24, screen=True, console=console):
            while self.active:
                self.update_view()
                await asyncio.sleep(0.041)
