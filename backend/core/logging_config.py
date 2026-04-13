import logging
import os
import queue
import json
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from logging import Filter, LogRecord
from rich.logging import RichHandler
from rich.console import Console

console = Console()

class PacketRedactorFilter(Filter):
    """Sanitizes internal IP and MAC addresses to prevent network topology leakage."""
    import re
    IP_PATTERN = re.compile(r"\b(?:172\.(?:1[6-9]|2[0-9]|3[0-1])\.|192\.168\.|10\.)[0-9]{1,3}\.[0-9]{1,3}\b")
    MAC_PATTERN = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b")

    def filter(self, record: LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.IP_PATTERN.sub("[REDACTED_IP]", record.msg)
            record.msg = self.MAC_PATTERN.sub("[REDACTED_MAC]", record.msg)
        return True

class JSONFormatter(logging.Formatter):
    """Vectorized JSON serialization for asynchronous log writing."""
    def format(self, record: LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage()
        }
        return json.dumps(log_obj)

class ForensicsThreatFilter(Filter):
    """Routes high-priority neural summaries to the dedicated chronicle vault."""
    def filter(self, record: LogRecord) -> bool:
        return record.levelno >= logging.WARNING or "CRITICAL" in record.getMessage()

def setup_observability() -> QueueListener:
    """Instantiates the asynchronous, multi-channel structural persistence layer."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(base_dir, "logs")
    forensic_dir = os.path.join(base_dir, "forensics")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(forensic_dir, exist_ok=True)

    # 1. Rich Handler for Terminal Viewport (Ocular HUD)
    rich_handler = RichHandler(console=console, rich_tracebacks=True, markup=True, show_time=True, show_path=False)
    
    # 2. General Diagnostic JSON Handler (Rotation-Aware <150MB constraint)
    json_path = os.path.join(log_dir, "coregraph_diagnostic.jsonl")
    json_handler = RotatingFileHandler(json_path, maxBytes=10*1024*1024, backupCount=5)
    json_handler.setFormatter(JSONFormatter())

    # 3. High-Priority Forensic Chronicle Handler
    threat_path = os.path.join(forensic_dir, "threat_chronicle.log")
    threat_handler = RotatingFileHandler(threat_path, maxBytes=20*1024*1024, backupCount=3)
    threat_formatter = logging.Formatter("[%(asctime)s] NEURAL-ALERT | %(levelname)s | %(message)s")
    threat_handler.setFormatter(threat_formatter)
    threat_handler.addFilter(ForensicsThreatFilter())

    # Add general redactor filter
    redactor = PacketRedactorFilter()
    for h in [rich_handler, json_handler, threat_handler]:
        h.addFilter(redactor)

    # Asynchronous Queue Integration
    log_queue = queue.Queue(-1)
    queue_handler = QueueHandler(log_queue)
    
    # Root Logger Config
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(queue_handler)

    # Listener manages the background I/O thread
    listener = QueueListener(log_queue, rich_handler, json_handler, threat_handler, respect_handler_level=True)
    listener.start()
    return listener

# Global singleton initializer starting the non-blocking background archiver
logger_listener = setup_observability()

