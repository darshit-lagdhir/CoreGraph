import logging

logger = logging.getLogger(__name__)


class HUDSync:
    """
    Sovereign Telemetry Bridge: Bridges backend logic to the Radiant HUD.
    """

    def __init__(self):
        self.active = True

    def log_info(self, msg: str):
        logger.info(f"[HUD] {msg}")

    def log_success(self, msg: str):
        logger.info(f"[HUD][SUCCESS] {msg}")

    def log_warning(self, msg: str):
        logger.warning(f"[HUD][WARNING] {msg}")

    def log_error(self, msg: str):
        logger.error(f"[HUD][ERROR] {msg}")

    def log_event(self, event_type: str, data: dict):
        logger.info(f"[HUD_EVENT][{event_type}] {data}")
