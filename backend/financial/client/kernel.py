import asyncio
import ssl
import time
import random
import logging
import psutil
import aiohttp
from typing import Optional, Dict, Any, List

logger = logging.getLogger("coregraph.financial.transport")


class HUDDiagnosticSignalBridge:
    """
    Module 6 - Task 001: 144Hz Network-to-HUD Sync Manifold.
    Non-blocking signal emitter to push latency and throughput states to the primary UI.
    """

    __slots__ = ("_active_sockets", "_total_bytes", "_stutter_events")

    def __init__(self) -> None:
        self._active_sockets: int = 0
        self._total_bytes: int = 0
        self._stutter_events: int = 0

    def register_socket_acquisition(self) -> None:
        self._active_sockets += 1

    def register_socket_release(self, bytes_received: int, latency_ms: float) -> None:
        self._active_sockets = max(0, self._active_sockets - 1)
        self._total_bytes += bytes_received

    def record_tier_throttling(self) -> None:
        self._stutter_events += 1

    def emit_diagnostics(self) -> Dict[str, Any]:
        return {
            "active_sockets": self._active_sockets,
            "transferred_bytes": self._total_bytes,
            "stutter_events": self._stutter_events,
        }


def _create_pinned_tls_context() -> ssl.SSLContext:
    """Enforce strict TLS 1.3 to prevent cryptographic anomaly vectors."""
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    # Explicitly prohibit legacy protocol handshake
    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    return ctx


class TierAwareTransportPacer:
    """
    Evaluates Event Loop latency against the 144Hz HUD requirements (8ms threshold).
    Injects Wait-States to preserve frame liquid vision on Potato-tier hardware.
    """

    __slots__ = ("_last_tick", "_threshold_seconds")

    def __init__(self, target_hz: int = 144) -> None:
        self._last_tick: float = time.monotonic()
        self._threshold_seconds: float = 1.0 / target_hz

    async def synchronize_frame(self, diagnostic_bridge: HUDDiagnosticSignalBridge) -> None:
        current_tick = time.monotonic()
        delta = current_tick - self._last_tick

        if delta > self._threshold_seconds:
            # HUD stutter detected; yield entirely to allow UI thread clearance
            diagnostic_bridge.record_tier_throttling()
            await asyncio.sleep(0.005)

        self._last_tick = time.monotonic()


class FinancialClientKernel:
    """
    Module 6 - Task 001: The Asynchronous Financial Ledger Client.
    Pure async transport layer for open-source economic metric extraction.
    """

    __slots__ = (
        "_hardware_tier",
        "_pool_limit",
        "_ssl_context",
        "_diagnostic_bridge",
        "_pacer",
        "_connector",
        "_session",
        "_user_agents",
        "_max_payload_bytes",
    )

    def __init__(self) -> None:
        self._hardware_tier = self._detect_hardware_tier()
        self._pool_limit = 500 if self._hardware_tier == "REDLINE" else 10
        self._max_payload_bytes = 5 * 1024 * 1024  # 5MB buffer truncation limit

        self._diagnostic_bridge = HUDDiagnosticSignalBridge()
        self._pacer = TierAwareTransportPacer()
        self._ssl_context = _create_pinned_tls_context()

        # Hardened, anonymizing agent rotation pool
        self._user_agents: List[str] = [
            "CoreGraph-Titan-Probe/v6.0 (Enterprise OSINT)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        ]

        self._connector: Optional[aiohttp.TCPConnector] = None
        self._session: Optional[aiohttp.ClientSession] = None

    def _detect_hardware_tier(self) -> str:
        """Determines physical constraints to select Connection Pool gearbox size."""
        cores = psutil.cpu_count(logical=False) or 2
        ram_gb = psutil.virtual_memory().total / (1024**3)
        if cores >= 8 and ram_gb >= 32.0:
            return "REDLINE"
        return "POTATO"

    async def initialize_transport_pool(self) -> None:
        """Ignites the TCP pool with connection persistance configuration."""
        if self._session is not None:
            return

        # Fallback to pure ThreadedResolver to avoid Windows/aiodns routing anomalies in containerized testing
        resolver = aiohttp.ThreadedResolver()

        self._connector = aiohttp.TCPConnector(
            limit=self._pool_limit,
            limit_per_host=min(self._pool_limit, 50),
            ssl=self._ssl_context,
            keepalive_timeout=60.0 if self._hardware_tier == "REDLINE" else 15.0,
            enable_cleanup_closed=True,
            resolver=resolver,
        )

        timeout = aiohttp.ClientTimeout(total=10.0, connect=3.0, sock_read=5.0)

        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=timeout,
            auto_decompress=True,
        )
        logger.info(
            f"Financial Transport Pool ignited. Gearbox: {self._hardware_tier} "
            f"[C_socket={self._pool_limit}]"
        )

    async def extract_financial_ledger_raw(self, endpoint_url: str) -> bytes:
        """
        Executes a wait-free financial probe.
        Strictly returns RAW BYTES to bypass dynamic float coercion prior to Decimal injection.
        """
        if self._session is None:
            raise RuntimeError("Transport pool is not ignited.")

        agent = random.choice(self._user_agents)
        headers = {"User-Agent": agent, "Accept": "application/json", "Connection": "keep-alive"}

        # Sync with 144Hz HUD manifold before launching extraction
        await self._pacer.synchronize_frame(self._diagnostic_bridge)

        self._diagnostic_bridge.register_socket_acquisition()
        start_time = time.monotonic()
        transferred_bytes = 0

        try:
            async with self._session.get(endpoint_url, headers=headers) as response:
                response.raise_for_status()

                # Read raw stream safely under buffer limits (Buffer Overflow Defense)
                raw_bytes = await response.content.read(self._max_payload_bytes)
                transferred_bytes = len(raw_bytes)

                if not response.content.at_eof():
                    raise ValueError(
                        f"Payload Exceeds Structural Quota of {self._max_payload_bytes} bytes."
                    )

                return raw_bytes

        except aiohttp.ClientError as transport_err:
            logger.error(f"Strategic Transport Anomaly at {endpoint_url}: {str(transport_err)}")
            raise
        finally:
            latency_ms = (time.monotonic() - start_time) * 1000.0
            self._diagnostic_bridge.register_socket_release(transferred_bytes, latency_ms)

    async def close_pool(self) -> None:
        """Forcefully collapses the socket connection state to reclaim heap residency."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        self._connector = None
        logger.info("Financial Transport Pool safely collapsed.")
