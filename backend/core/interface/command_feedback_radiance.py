from rich.text import Text


class CommandFeedbackRadiance:
    """
    SECTOR ZETA: Chromatic Feedback Loop.
    Projects visual confirmation of agentic action success or failure.
    """

    def __init__(self):
        self.history: list = []

    def log_success(self, command: str, result: str) -> Text:
        """Sector Zeta: Cyan Pulse for success."""
        entry = Text.assemble(
            ("> ", "cyan bold"), (f"{command}: ", "white"), (result, "cyan italic")
        )
        self.history.append(entry)
        return entry

    def log_failure(self, command: str, error: str) -> Text:
        """Sector Zeta: Amber Flicker for anomaly."""
        entry = Text.assemble(
            ("! ", "orange3 bold"), (f"{command}: ", "white"), (error, "orange3 italic")
        )
        self.history.append(entry)
        return entry

    def get_history(self, limit: int = 5) -> list:
        return self.history[-limit:]
