import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Set, Tuple


class TelemetryRecord:
    """
    Slotted DTO enforcing the Unified CoreGraph Telemetry Schema constraints.
    Zero-Loss format buffering standard normalized intelligence and unmapped JSONB overflows.
    """

    __slots__ = (
        "purl",
        "internal_id",
        "timestamp",
        "commit_velocity",
        "active_maintainer_count",
        "issue_resolution_latency",
        "forensic_overflow",
    )

    def __init__(self, purl: str, internal_id: str):
        self.purl = purl
        self.internal_id = internal_id
        self.timestamp = time.time()
        self.commit_velocity = 0.0
        self.active_maintainer_count = 0
        self.issue_resolution_latency = 0.0
        self.forensic_overflow: Dict[str, Any] = {}


class DLQArchivalPacket:
    """
    Slotted packet tracking the Forensic Archival Handshake variables.
    Prepared for synchronous database insertions capturing terminal registry failures.
    """

    __slots__ = ("purl", "alias", "error_code", "message", "batch_uuid", "timestamp")

    def __init__(self, purl: str, alias: str, error_code: str, message: str, batch_uuid: str):
        self.purl = purl
        self.alias = alias
        self.error_code = error_code
        self.message = message
        self.batch_uuid = batch_uuid
        self.timestamp = time.time()


class TelemetryResponseParser:
    """
    Module 5 - Task 012: Asynchronous GraphQL Response Parser.
    Extracts, Disambiguates, and Normalizes registry payloads using iterative extraction sweeps
    and Partial Failure 'Forensic Handshake' mappings.
    """

    __slots__ = (
        "_hardware_tier",
        "_alias_registry",
        "_dlq_buffer",
        "_yield_threshold",
        "_is_shutting_down",
    )

    def __init__(self, alias_registry: Dict[str, Dict[str, str]], hardware_tier: str = "redline"):
        self._hardware_tier = hardware_tier
        self._alias_registry = alias_registry
        self._dlq_buffer: List[DLQArchivalPacket] = []
        self._is_shutting_down = False

        # Hardware-Aware Heap Yield Configurations
        if self._hardware_tier == "redline":
            self._yield_threshold = 20
        else:
            self._yield_threshold = 5

    def _resolve_forensic_context(self, alias: str) -> Tuple[Optional[str], Optional[str]]:
        """
        O(1) Bridge crossing from volatile GraphQL Identity to Permanent Vault Coordinates.
        """
        context = self._alias_registry.get(alias)
        if not context:
            logging.error(f"[DISAMBIGUATION FAULT] Alias {alias} lacks active relational mapping.")
            return None, None
        return context.get("purl"), context.get("internal_id")

    def process_graphql_errors(
        self, errors_array: List[Dict[str, Any]], batch_uuid: str
    ) -> Set[str]:
        """
        Partial Failure Resolution Kernel.
        Mines standard error paths to map specific failing sub-queries against their PURLs,
        neutralizes block-level failures to protect neighboring success payloads.
        """
        failed_aliases = set()
        for error in errors_array:
            path = error.get("path", [])
            message = error.get("message", "UNKNOWN_ERROR")
            error_type = error.get("extensions", {}).get("code", "GENERAL_FAILURE")

            if not path:
                continue

            # Alias sits natively at array 0 in telemetry builder configurations
            alias = path[0]
            failed_aliases.add(alias)

            purl, _ = self._resolve_forensic_context(alias)
            if not purl:
                continue

            # Telemetry Strategic Routing via Exception Fingerprints
            if (
                "NOT_FOUND" in error_type
                or "FORBIDDEN" in error_type.upper()
                or "NOT_ACCESSIBLE" in error_type
            ):
                packet = DLQArchivalPacket(purl, alias, error_type, message, batch_uuid)
                self._dlq_buffer.append(packet)
            elif "TIMEOUT" in error_type or "MAX_NODE_LIMIT" in error_type.upper():
                logging.warning(
                    f"[RECOVERABLE ANOMALY] Node {purl} triggered complexity bounds. Triggering governor reset."
                )

        return failed_aliases

    def normalize_telemetry(
        self, raw_data: Dict[str, Any], purl: str, internal_id: str
    ) -> TelemetryRecord:
        """
        Translates targeted JSON Dictionary depths into flat schema properties while
        preservating unmatched metrics to the JSONB buffer.
        """
        record = TelemetryRecord(purl, internal_id)

        # Primary Telemetry Target Resolution Simulation Layer
        repo_data = raw_data.get("repository", {})
        if repo_data:
            record.commit_velocity = repo_data.get("velocity_metric", 0.0)
            record.active_maintainer_count = repo_data.get("maintainer_count", 0)

        # Zero-Loss Overflow Capture
        handled_keys = {"velocity_metric", "maintainer_count"}
        record.forensic_overflow = {k: v for k, v in repo_data.items() if k not in handled_keys}

        return record

    async def parse_response_stream(
        self, payload: Dict[str, Any], batch_uuid: str
    ) -> AsyncGenerator[TelemetryRecord, None]:
        """
        Iterative Data Stream Extractor.
        Leverages strict dictionary key yields and automated variable discarding paired
        with explicitly bound asyncio sleeps to prevent Single-Thread HUD locking.
        """
        failed_aliases: Set[str] = set()

        if "errors" in payload and payload["errors"]:
            failed_aliases = self.process_graphql_errors(payload["errors"], batch_uuid)

        data_blocks = payload.get("data", {})
        if not data_blocks:
            return

        iteration_count = 0

        for alias, block_data in data_blocks.items():
            if self._is_shutting_down:
                break

            if alias in failed_aliases or block_data is None:
                continue

            purl, internal_id = self._resolve_forensic_context(alias)
            if not purl or not internal_id:
                continue

            record = self.normalize_telemetry(block_data, purl, internal_id)
            yield record

            # Flush specific dict memory references to enforce Flat Heap behavior on large structures
            del block_data

            iteration_count += 1
            if iteration_count % self._yield_threshold == 0:
                await asyncio.sleep(0)  # Hardware-Aware HUD Breathing Room

        del payload

    def mandate_shutdown(self) -> None:
        """Trigger graceful stream parser truncation."""
        self._is_shutting_down = True
