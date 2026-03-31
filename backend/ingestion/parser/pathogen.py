import math
from typing import Dict, Any, List, Optional, Tuple


class PathogenIdentifier:
    __slots__ = (
        "hardware_tier",
        "_foundation_registry",
        "_maintainer_baseline",
        "_entropy_threshold",
        "_hud_signal_bus",
        "_weights",
    )

    def __init__(self, hardware_tier: str):
        self.hardware_tier = hardware_tier
        self._foundation_registry: List[str] = []
        self._maintainer_baseline: Dict[str, str] = {}

        if self.hardware_tier == "redline":
            self._entropy_threshold = 4.8
            self._weights = {"entropy": 0.3, "identity": 0.4, "topo": 0.1, "naming": 0.2}
        else:
            self._entropy_threshold = 5.2
            self._weights = {"entropy": 0.4, "identity": 0.3, "topo": 0.0, "naming": 0.3}

        self._hud_signal_bus: List[Dict[str, Any]] = []

    def set_foundation_registry(self, top_packages: List[str]) -> None:
        self._foundation_registry = sorted(top_packages)

    def set_maintainer_baseline(self, pkg_name: str, baseline_email: str) -> None:
        self._maintainer_baseline[pkg_name] = baseline_email

    def _calculate_entropy(self, text: str) -> float:
        if not text:
            return 0.0

        length = len(text)
        if length > 5000 and self.hardware_tier != "redline":
            text = text[:5000]
            length = 5000

        frequencies: Dict[str, int] = {}
        for char in text:
            frequencies[char] = frequencies.get(char, 0) + 1

        entropy = 0.0
        for count in frequencies.values():
            prob = count / length
            entropy -= prob * math.log2(prob)

        return entropy

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def _check_typosquatting(self, package_name: str) -> Tuple[bool, Optional[str]]:
        if package_name in self._foundation_registry:
            return False, None

        if self.hardware_tier != "redline":
            sliced_registry = self._foundation_registry[:500]
        else:
            sliced_registry = self._foundation_registry

        for foundation_pkg in sliced_registry:
            dist = self._levenshtein_distance(package_name, foundation_pkg)
            if 0 < dist <= 2 and len(foundation_pkg) > 4:
                return True, foundation_pkg

        return False, None

    def _check_maintainer_drift(self, package_name: str, current_email: str) -> bool:
        baseline = self._maintainer_baseline.get(package_name)
        if not baseline:
            return False

        if not current_email:
            return True

        base_domain = baseline.split("@")[-1] if "@" in baseline else baseline
        curr_domain = current_email.split("@")[-1] if "@" in current_email else current_email

        if base_domain != curr_domain:
            return True

        return False

    def scan_payload(self, package_name: str, raw_payload: Dict[str, Any]) -> int:
        r_e = 0.0
        r_i = 0.0
        r_t = 0.0
        r_n = 0.0

        flags = 0

        description = raw_payload.get("description", "")
        if description:
            ent = self._calculate_entropy(description)
            if ent > self._entropy_threshold:
                r_e = 1.0
                flags |= 1 << 0

        is_typo, target = self._check_typosquatting(package_name)
        if is_typo:
            r_n = 1.0
            flags |= 1 << 1

        maintainer = raw_payload.get("maintainer_email", "")
        if self._check_maintainer_drift(package_name, maintainer):
            r_i = 1.0
            flags |= 1 << 2

        dep_count = len(raw_payload.get("dependencies", {}))
        if dep_count > 50 and self.hardware_tier == "redline":
            r_t = 1.0
            flags |= 1 << 3

        p_idx_raw = (
            self._weights["entropy"] * r_e
            + self._weights["identity"] * r_i
            + self._weights["topo"] * r_t
            + self._weights["naming"] * r_n
        )

        scaled_score = min(int(p_idx_raw * 100), 100)

        if scaled_score > 30:
            self._dispatch_anomaly_signal(package_name, scaled_score, flags)

        return flags

    def _dispatch_anomaly_signal(self, package_name: str, risk_score: int, flags: int) -> None:
        signal = {
            "coordinate": package_name,
            "risk_score": risk_score,
            "flags": flags,
            "timestamp": "immediate",
        }
        self._hud_signal_bus.append(signal)

    def extract_hud_signals(self) -> List[Dict[str, Any]]:
        signals = self._hud_signal_bus.copy()
        self._hud_signal_bus.clear()
        return signals
