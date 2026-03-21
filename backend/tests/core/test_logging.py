import pytest
import json
import uuid
import time
import logging
from core.logging_config import correlation_id_var, setup_observability


def test_json_logging_schema_compliance(tmp_path):
    # Failure 3 Resolution: Verification of machine-readable structured output
    log_file = tmp_path / "test.jsonl"
    from concurrent_log_handler import ConcurrentRotatingFileHandler

    handler = ConcurrentRotatingFileHandler(str(log_file), "a", 1000, 1)

    from core.logging_config import JSONFormatter

    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("test_schema")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    test_id = str(uuid.uuid4())
    correlation_id_var.set(test_id)

    logger.info("TOPOLOGICAL_PROBE_INITIALIZED", extra={"node_count": 100})

    # Ensuring the flush completes before sampling
    handler.flush()
    handler.close()

    with open(log_file, "r") as f:
        line = f.readline()
        data = json.loads(line)

        assert "timestamp" in data
        assert "correlation_id" in data
        assert data["correlation_id"] == test_id
        assert data["level"] == "INFO"
        assert data["message"] == "TOPOLOGICAL_PROBE_INITIALIZED"


def test_non_blocking_telemetry_throughput():
    # Failure 3 Resolution: Non-blocking Queue-based performance validation
    # This ensures that logging 10k items doesn't stall the event loop
    logger = logging.getLogger("test_perf")
    setup_observability()

    start_time = time.perf_counter()
    for i in range(1000):
        logging.info(f"HIGH_FREQUENCY_TRAVERSE_{i}")

    end_time = time.perf_counter()
    duration = end_time - start_time
    # Assertion: 1,000 logs should execute in < 0.1s on the i9 core
    assert duration < 0.1
