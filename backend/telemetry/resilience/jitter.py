import time
import secrets
import math
import collections
from typing import List


class CryptographicJitterKernel:
    """
    Module 5 - Task 013: Cryptographic Jitter and Asynchronous Slot Synchronization.
    The 'Acoustic Dampener' of the telemetry phalanx minimizing Temporal Resonance using
    CSPRNG pools and Hardware-Aware Wait-Time Coalescing.
    """

    __slots__ = (
        "_hardware_tier",
        "_slot_resolution_sec",
        "_resonance_history",
        "_resonance_window_sec",
        "_resonance_threshold",
        "_current_expansion_multiplier",
        "_csprng",
    )

    def __init__(self, hardware_tier: str = "redline"):
        self._hardware_tier = hardware_tier
        self._csprng = secrets.SystemRandom()

        # Hardware-Aware Temporal Gear-Box Configuration
        if self._hardware_tier == "redline":
            self._slot_resolution_sec = 0.010  # 10ms High-Resolution Entropy
            self._resonance_threshold = 20  # Max Wakeups per window
        else:
            self._slot_resolution_sec = 0.250  # 250ms Coarse Coalescing
            self._resonance_threshold = 10

        self._resonance_window_sec = 1.0  # Evaluate density within 1-second rolling buckets
        self._resonance_history: collections.deque = collections.deque(maxlen=1000)
        self._current_expansion_multiplier = 1.0

    def calculate_jittered_delay(
        self, base_delay: float, priority_coefficient: float = 1.0
    ) -> float:
        """
        'Full Jitter' CSPRNG Engine resolving strict Uniform distribution mapped inside
        an expanding resonance-aware probability frame.
        """
        # Audit Current Temporal Density for Resonance Handshake
        self._monitor_temporal_density()

        # Inject tactical priority bound and algorithmic widening limit
        upper_bound = base_delay * priority_coefficient * self._current_expansion_multiplier

        # Pull mathematically sound uniform floating-point integer
        raw_jitter = self._csprng.uniform(0.0, upper_bound)

        # Round the entropy payload into distinct CPU batch epochs avoiding interrupt storms
        slot_aligned_delay = self.synchronize_to_slot(raw_jitter)

        self._record_temporal_event(slot_aligned_delay)
        return slot_aligned_delay

    def synchronize_to_slot(self, target_epoch: float) -> float:
        """
        Determines the 'Coalesced Timing' bracket for CPU interrupt clustering.
        Ensures dozens of task retries share the precise same wake millisecond avoiding GIL block.
        """
        # Round payload logic preserving strict hardware ceiling intervals
        multiples = target_epoch / self._slot_resolution_sec
        return math.ceil(multiples) * self._slot_resolution_sec

    def _record_temporal_event(self, delta_delay: float) -> None:
        """Appends future wake-up epoch natively to history frame."""
        future_epoch = time.time() + delta_delay
        self._resonance_history.append(future_epoch)

    def _monitor_temporal_density(self) -> None:
        """
        The Systemic Resonance Detector.
        Analyzes the sliding temporal window identifying incoming Thundering Herd logic collisions.
        Triggers exponential variance boundaries if structural bot-blocking is suspected.
        """
        current_time = time.time()

        # Prune expired epochs cleanly mapping O(1) side-effects
        while (
            self._resonance_history
            and self._resonance_history[0] < current_time - self._resonance_window_sec
        ):
            self._resonance_history.popleft()

        # Density check across the active temporal slice
        active_wakeups_pending = sum(
            1
            for epoch in self._resonance_history
            if current_time <= epoch <= current_time + self._resonance_window_sec
        )

        if active_wakeups_pending > self._resonance_threshold:
            # Dangerous Density Level Reached - Force Entropy Widening Phase
            self._current_expansion_multiplier = min(self._current_expansion_multiplier * 1.5, 5.0)
        else:
            # Equilibrium State - Normalize Distribution Limits
            self._current_expansion_multiplier = max(self._current_expansion_multiplier * 0.9, 1.0)

    def extract_entropy_vitality(self) -> dict:
        """
        Prepares the Temporal Vitality Object pushing metrics natively to HUD.
        """
        return {
            "slot_saturation_estimate": len(self._resonance_history),
            "resonance_multiplier": self._current_expansion_multiplier,
            "slot_resolution": self._slot_resolution_sec,
        }
