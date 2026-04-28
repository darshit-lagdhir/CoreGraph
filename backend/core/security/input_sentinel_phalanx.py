import re
import logging
from typing import Set, Optional

logger = logging.getLogger(__name__)


class InputSentinelPhalanx:
    """
    SECTOR GAMMA: Input Sentinel Phalanx.
    Intercepts and filters every keystroke to protect the Sovereign Kernel.
    """

    def __init__(self):
        # Sector Gamma: Rigid Command Whitelist
        self.allowed_commands: Set[str] = {
            "SCAN",
            "TRACE",
            "FILTER",
            "ZOOM",
            "PAN",
            "INFO",
            "ZENITH",
        }
        self.input_buffer = ""
        self.blocked_attempts = 0

    def filter_input(self, char: str) -> Optional[str]:
        """
        Sector Gamma: Websocket-layer Key Interception.
        Neutralizes escape sequences, pipes, and control characters.
        """
        # Temporal Entropy Filter simulation (Sector Alpha)
        # In a real environment, this would check timing; here we filter malicious ASCII.
        if char in ("\x03", "\x04", "\x1a", "|", ">", "<", "&", ";", "$"):
            self.blocked_attempts += 1
            logger.warning(f"[Gamma] MALICIOUS_INPUT_BLOCKED: {hex(ord(char))}")
            return None

        # We only allow standard alphanumeric and forensic query chars
        if not re.match(r"[a-zA-Z0-9\s_\-\[\]\.]", char):
            return None

        return char

    def validate_command(self, cmd: str) -> bool:
        """Verifies the command against the Lexical Guard."""
        cmd_upper = cmd.strip().upper()
        return any(cmd_upper.startswith(allowed) for allowed in self.allowed_commands)
