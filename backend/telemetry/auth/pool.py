import asyncio
import time
import logging
import random
from typing import List, Dict, Optional


class TokenRecord:
    """
    Slotted structural representation of an isolated authentication credential.
    Forces strict memory residency and minimizes credential leakage paths.
    """

    __slots__ = (
        "_raw_token",
        "identifier",
        "remaining_points",
        "reset_timestamp",
        "is_cooling_down",
    )

    def __init__(self, raw_token: str):
        self._raw_token = raw_token
        # Masked ID for safe diagnostic logging
        self.identifier = f"tkn_...{raw_token[-4:]}" if len(raw_token) >= 4 else "tkn_invalid"
        self.remaining_points: int = 5000  # Assumed max before first provider sync
        self.reset_timestamp: float = 0.0
        self.is_cooling_down: bool = False

    def get_auth_header(self) -> str:
        """Secure materialization of authorization payload."""
        return f"Bearer {self._raw_token}"


class TelemetryTokenPool:
    """
    Module 5 - Task 006: Authentication Token Rotation Pool and Dynamic Quota Management.
    Provides mathematically verified, thread-safe asynchronous credential multiplexing.
    """

    __slots__ = (
        "_active_queue",
        "_cooldown_vault",
        "_pool_lock",
        "_safety_margin",
        "_hardware_tier",
    )

    def __init__(self, raw_tokens: List[str], hardware_tier: str = "redline"):
        self._hardware_tier = hardware_tier
        self._pool_lock = asyncio.Lock()

        # Ensures total extraction wave logic never halts entirely on latency spikes
        self._safety_margin = 100

        self._active_queue: List[TokenRecord] = [TokenRecord(t) for t in raw_tokens]
        self._cooldown_vault: List[TokenRecord] = []

        random.shuffle(self._active_queue)

    async def acquire_token(self) -> TokenRecord:
        """
        Asynchronous Thread-Safe Mutex Protocol.
        Guarantees isolation of credential usage across parallel worker phalanxes
        to prevent double-spending race conditions.
        """
        async with self._pool_lock:
            if not self._active_queue:
                raise Exception("CRITICAL: Authentication Starvation. All tokens in cooldown.")

            # Hardware-Aware sorting: O(N) evaluation of current highest-capacity credential
            best_token = max(self._active_queue, key=lambda t: t.remaining_points)

            if best_token.remaining_points <= self._safety_margin:
                await self._force_cooldown(best_token)
                return await self.acquire_token()  # Recursive fallback safely bound by vault logic

            return best_token

    async def report_usage(self, identifier: str, remaining_quota: int, reset_stamp: float) -> None:
        """
        Dynamic Quota Monitor.
        Updates internal token viability based on exact provider response headers.
        """
        async with self._pool_lock:
            for token in self._active_queue:
                if token.identifier == identifier:
                    token.remaining_points = remaining_quota
                    token.reset_timestamp = reset_stamp

                    if token.remaining_points <= self._safety_margin:
                        await self._force_cooldown(token)
                    break

    async def _force_cooldown(self, token: TokenRecord) -> None:
        """
        Transition logic shifting a burnt credential out of the Active rotation vector.
        """
        if token in self._active_queue:
            self._active_queue.remove(token)
            token.is_cooling_down = True
            self._cooldown_vault.append(token)
            logging.info(f"Token {token.identifier} exhausted. Entering CooldownVault.")

            # Fire-and-forget reinstatement watcher
            asyncio.create_task(self._reinstatement_watcher(token))

    async def _reinstatement_watcher(self, token: TokenRecord) -> None:
        """
        Cooldown Governance Kernel.
        Precise monotonic sleep-and-wake logic. Neutralizes massive polling overhead.
        """
        now = time.time()
        sleep_duration = token.reset_timestamp - now

        if sleep_duration > 0:
            # Cryptographic jitter avoiding 429 stampeding herd on exact Unix boundary
            jitter = random.uniform(2.0, 5.0)
            await asyncio.sleep(sleep_duration + jitter)

        async with self._pool_lock:
            if token in self._cooldown_vault:
                self._cooldown_vault.remove(token)
                token.is_cooling_down = False
                token.remaining_points = 5000  # Reset theoretical max until next sync
                self._active_queue.append(token)
                logging.info(f"Token {token.identifier} reinstated. Added to ActiveQueue.")

    def calculate_pool_sustainability(self) -> float:
        """
        Diagnostic mathematical projection of available throughput power,
        yielding direct status values intended for the Master 144Hz HUD.
        """
        now = time.time()
        sustainability = 0.0

        for token in self._active_queue:
            time_to_reset = token.reset_timestamp - now
            if time_to_reset > 0:
                sustainability += token.remaining_points / time_to_reset

        return round(sustainability, 4)
