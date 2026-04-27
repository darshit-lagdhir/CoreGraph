from textual.widgets import DirectoryTree
from textual.message import Message
from backend.telemetry.hud_sync import HUDSync


class IngressExplorer(DirectoryTree):
    """
    REACTIVE HUD SIDEBAR: Visualizes the internal ingress directory.
    """

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)
        self.hud = HUDSync()

    def on_mount(self):
        self.border_title = "INGRESS PERIMETER"
        self.border_subtitle = "ENTROPY SENSING ACTIVE"

    async def on_directory_tree_file_selected(self, event):
        """Tactile Interface: Clicking a shard triggers deep forensic analysis."""
        file_path = str(event.path)
        self.hud.log_info(f"SIDEBAR: Focusing on shard {file_path}")
        # Trigger Unified Visual Link to Hadronic Matrix
        self.post_message(self.FocusShard(file_path))

    class FocusShard(Message):
        """Custom message to highlight nodes in the central matrix."""

        def __init__(self, path: str):
            super().__init__()
            self.path = path
