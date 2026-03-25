import hashlib
import hmac
import random
import base64
from datetime import datetime, timedelta
from typing import List, Tuple, Any, Optional, Dict
from pydantic import BaseModel

class SemVerState(BaseModel):
    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def update(self, prob_matrix: Tuple[float, float, float], state: Any):
        roll = state.random()
        if roll < prob_matrix[0]: # Patch
            self.patch += 1
        elif roll < prob_matrix[0] + prob_matrix[1]: # Minor
            self.minor += 1
            self.patch = 0
        else: # Major
            self.major += 1
            self.minor = 0
            self.patch = 0

class DeterministicGenerator:
    """
    The 'cg-sim-gen' Procedural Engine (Task 002 & 003).
    Implements Hash-Chaining Seeding, Telemetry, and Pagination.
    """
    def __init__(self, master_seed: int):
        self.master_seed = str(master_seed).encode()
        self.adjectives = ["core", "fast", "async", "safe", "global", "smart", "super", "micro"]
        self.nouns = ["sync", "proxy", "wrapper", "node", "graph", "vault", "stream", "engine"]

    def get_sub_seed(self, name: str) -> bytes:
        """Deterministic Sub-Seal for cross-process consistency."""
        return hmac.new(self.master_seed, name.encode(), hashlib.sha256).digest()

    def generate_name(self, index: int) -> str:
        state = random.Random(self.master_seed + str(index).encode())
        return f"{state.choice(self.adjectives)}-{state.choice(self.nouns)}-{state.randint(100, 999)}"

    # 1. TELEMETRY SYNTHESIS (Task 003)
    # Poisson arrival for commits | Lognormal for issues
    def generate_repo_telemetry(self, pkg_name: str) -> Dict[str, Any]:
        """Synthesizes Behavioral Signatures (Commit Velocity, Stars, Reputation)."""
        sub_seed = self.get_sub_seed(pkg_name)
        state = random.Random(sub_seed)

        # Power-Law (Zipfian) Social Proof
        stargazers = int(10**state.uniform(0, 5)) # 1 to 100,000 stars
        forks = int(stargazers * state.uniform(0.01, 0.2))

        # Poisson Commit Velocity (lambda = 1 to 20 commits/month)
        commit_lambda = state.uniform(1.0, 20.0)

        # Maintainer ID (consistent per package)
        maintainer_id = f"synth-dev-{sub_seed[:4].hex()}"
        reputation = state.randint(0, 100) # 0-100 score

        return {
            "name": pkg_name,
            "stargazerCount": stargazers,
            "forkCount": forks,
            "owner": {
                "login": maintainer_id,
                "reputation": reputation,
                "bio": f"Architect of {pkg_name}. OSINT node {maintainer_id} (Sealed)."
            },
            "lambda_v": commit_lambda,
            "isArchived": state.random() < 0.05,
            "isVulnerable": reputation < 10 or stargazers > 50000 and state.random() < 0.01
        }

    # 2. CURSOR PAGINATION PROTOCOL (Task 003)
    # Seed-Anchored Opaque Cursors
    def generate_cursor(self, index: int) -> str:
        """Generates an opaque, HMAC-signed pagination cursor."""
        # Signature: HMAC(Master_Seed, index) to prevent 'Pagination Desync'
        signature = hmac.new(self.master_seed, str(index).encode(), hashlib.sha256).hexdigest()[:8]
        raw_cursor = f"commit_{index}_{signature}"
        return base64.b64encode(raw_cursor.encode()).decode()

    def decode_cursor(self, cursor_str: str) -> Optional[int]:
        """Decodes and validates a cursor's seed-anchor signature."""
        try:
            decoded = base64.b64decode(cursor_str.encode()).decode()
            parts = decoded.split("_")
            if len(parts) != 3: return None

            idx = int(parts[1])
            expected_sig = hmac.new(self.master_seed, str(idx).encode(), hashlib.sha256).hexdigest()[:8]

            if parts[2] != expected_sig:
                return None # Signature mismatch (Stale Cursor)

            return idx
        except:
            return None

    def generate_version_chain(self, pkg_name: str, count: int, start_date: datetime) -> List[dict]:
        sub_seed = self.get_sub_seed(pkg_name)
        state = random.Random(sub_seed)

        versions = []
        current_semver = SemVerState()
        current_date = start_date
        MATRIX = (0.70, 0.25, 0.05)

        for i in range(count):
            versions.append({
                "version": str(current_semver),
                "published_at": current_date.isoformat(),
                "dependencies": [],
                "metadata": {
                    "hash_sha256": hashlib.sha256(f"{pkg_name}@{current_semver}".encode()).hexdigest(),
                    "size_bytes": str(state.randint(1024, 10485760))
                }
            })
            current_semver.update(MATRIX, state)
            delta_days = int(-45 * state.uniform(0.1, 1.0))
            current_date += timedelta(days=max(1, delta_days))

        return versions
