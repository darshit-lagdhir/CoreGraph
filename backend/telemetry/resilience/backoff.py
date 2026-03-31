import asyncio
import time
import secrets
import logging
from typing import Dict, List, Any, Callable, Awaitable, Optional
from functools import wraps


class NetworkResilienceException(Exception):
    """Base exception for telemetry driver network failures."""

    def __init__(self, message: str, status_code: int = 500, retry_after: Optional[float] = None):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


class TerminalResourceNotFound(NetworkResilienceException):
    """Represents a 404 Not Found - bypasses backoff and goes directly to DLQ."""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class RegistryServiceUnavailable(NetworkResilienceException):
    """Represents a 503 Service Unavailable."""

    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class ProviderRateLimitExceeded(NetworkResilienceException):
    """Represents a 429 Too Many Requests."""

    def __init__(self, message: str, retry_after: float):
        super().__init__(message, status_code=429, retry_after=retry_after)


class DLQFailurePacket:
    """
    Slotted transactional packet capturing terminal network failures
    to preserve forensic integrity of dropped nodes natively.
    """

    __slots__ = ("purl", "exception_type", "history", "timestamp", "batch_uuid")

    def __init__(self, purl: str, exception_type: str, history: List[float], batch_uuid: str):
        self.purl = purl
        self.exception_type = exception_type
        self.history = history
        self.timestamp = time.time()
        self.batch_uuid = batch_uuid


class DeterministicBackoffKernel:
    """
    Module 5 - Task 011: Deterministic Exponential Backoff Kernel.
    Network Resilience Manifold enforcing geometric delay algorithms and CSPRNG jitter
    to protect CoreGraph clusters against provider throttling and thundering herds.
    """

    __slots__ = (
        "_hardware_tier",
        "_max_retries",
        "_base_delay",
        "_jitter_min",
        "_jitter_max",
        "_wait_registry",
        "_dlq_buffer",
        "_is_shutting_down",
    )

    def __init__(self, hardware_tier: str = "redline"):
        self._hardware_tier = hardware_tier
        self._wait_registry: Dict[int, float] = {}
        self._dlq_buffer: List[DLQFailurePacket] = []
        self._is_shutting_down = False

        # Hardware-Aware Resilience Gear-Box
        if self._hardware_tier == "redline":
            self._max_retries = 10
            self._base_delay = 0.25  # Aggressive Probing Base
            self._jitter_min = 0.5
            self._jitter_max = 1.0
        else:
            self._max_retries = 3
            self._base_delay = 1.0  # Potato/Conservative Base
            self._jitter_min = 0.2
            self._jitter_max = 1.2

    def _calculate_delay(self, attempt: int) -> float:
        """
        Executes the pure Geometric Progression delay formula mapped deeply
        with Cryptographic SystemRandom Jitter to eliminate temporal resonance.
        """
        geometric_base = self._base_delay * (2**attempt)
        # Bounded temporal recovery horizon protecting system event loops
        geometric_base = min(geometric_base, 60.0)
        cryptographic_jitter = secrets.SystemRandom().uniform(self._jitter_min, self._jitter_max)
        return geometric_base * cryptographic_jitter

    def _handoff_to_dlq(
        self, purl: str, exception: Exception, history: List[float], batch_uuid: str
    ) -> None:
        """
        Atomic relational packaging routing terminal unrecoverable domains
        into the Dead Letter Queue for explicit future human-analyst review.
        """
        packet = DLQFailurePacket(purl, type(exception).__name__, history, batch_uuid)
        self._dlq_buffer.append(packet)
        # logging.error(f"[DLQ HANDOFF] Terminal failure isolated. Node {purl} scheduled for fault-vault schema.")

    def retry_on_network_error(
        self,
        extract_purl_func: Callable[..., str],
        extract_batch_uuid_func: Callable[..., str] = lambda *args, **kwargs: "global_wave",
    ) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
        """
        Asynchronous Wait-Free Worker Bridge Decorator.
        Surgically traps `NetworkResilienceException` derivates avoiding GIL locks
        during Wait-States and feeding HUD telemetry metrics natively.
        """

        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                purl = extract_purl_func(*args, **kwargs)
                batch_uuid = extract_batch_uuid_func(*args, **kwargs)
                history: List[float] = []
                attempt = 0

                while attempt < self._max_retries and not self._is_shutting_down:
                    try:
                        return await func(*args, **kwargs)
                    except NetworkResilienceException as e:
                        # Surgical Exception Filtering
                        if getattr(e, "status_code", 500) == 404:
                            self._handoff_to_dlq(purl, e, history, batch_uuid)
                            raise e

                        # Tactical Retreat vs Geometric Survival Probe logic
                        retry_after = getattr(e, "retry_after", None)
                        if getattr(e, "status_code", 500) == 429 and retry_after is not None:
                            delay = float(retry_after)
                        else:
                            delay = self._calculate_delay(attempt)

                        history.append(delay)
                        current_task_ident = id(asyncio.current_task())
                        wake_epoch = time.time() + delay
                        self._wait_registry[current_task_ident] = wake_epoch

                        # Wait-Free Timer execution mapping back to asyncio scheduler core
                        await asyncio.sleep(delay)

                        self._wait_registry.pop(current_task_ident, None)
                        attempt += 1

                if attempt >= self._max_retries:
                    terminal_exc = Exception(
                        f"Resilience Exhausted: Terminal threshold breached for {purl}"
                    )
                    self._handoff_to_dlq(purl, terminal_exc, history, batch_uuid)
                    raise terminal_exc

            return wrapper

        return decorator

    def shutdown(self) -> None:
        """Flattens event limits enforcing pure destruction hooks."""
        self._is_shutting_down = True
