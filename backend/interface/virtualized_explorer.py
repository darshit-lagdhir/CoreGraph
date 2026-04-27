import os
import gc
from typing import Iterable
from pathlib import Path
from textual.widgets import DirectoryTree
from textual.widgets._directory_tree import DirEntry
from backend.telemetry.hud_sync import HUDSync
from backend.core.memory_manager import metabolic_governor


class VirtualizedExplorer(DirectoryTree):
    """
    VIRTUALIZED EXPLORER MANIFOLD: A lazy-loaded navigational aperture.
    Implements recursive eviction and metabolic discipline for 150MB RSS.
    """

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)
        self.hud = HUDSync()
        self.active_nodes = set()

    def on_mount(self):
        self.border_title = "HADRONIC INGRESS EXPLORER"
        self.border_subtitle = "VIRTUALIZED NAVIGATION ACTIVE"

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Sector Alpha: Filters out entropy noise before UI projection."""
        return [p for p in paths if not p.name.startswith(".")]

    def _on_tree_node_expanded(self, event):
        """Recursive Ingestion: Track expanded nodes for metabolic auditing."""
        self.active_nodes.add(event.node.id)
        self._audit_ui_metabolism()

    def _on_tree_node_collapsed(self, event):
        """Recursive Eviction: Purge collapsed branches from the widget tree."""
        if event.node.id in self.active_nodes:
            self.active_nodes.remove(event.node.id)

        # Sector Gamma: Force GC on collapsed branch metadata
        event.node._children = []
        gc.collect()
        self.hud.log_event("UI_EVICTION", {"node_id": str(event.node.id)})

    def _audit_ui_metabolism(self):
        """Sector Theta: Enforces the 25MB UI memory ceiling."""
        rss_mb = metabolic_governor.get_physical_rss_us()
        self.hud.log_event("UI_METABOLISM", {"rss_mb": rss_mb})

        if rss_mb > 145.0:  # Emergency Scythe
            self.hud.log_warning("UI_SCYTHE: Metabolic Limit Breach. Collapsing inactive branches.")
            self.collapse_all()
            gc.collect()

    def render_label(self, node, base_style, control_style):
        """Sector Eta: Spectral sparkline projection via chromatic overlays."""
        label = node.label.copy()
        path = str(node.data.path) if node.data else ""

        # Chromatic Depth: Vapor-Collapse Gold for Hardened Shards
        if "/vault/" in path:
            label.stylize("bold gold1")
            label.append(" [VAULT]", "dim")
        elif "/quarantine/" in path:
            label.stylize("bold red")
            label.append(" [⚠]", "blink")

        return label
