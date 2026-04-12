import time
import hmac
import hashlib
from typing import Dict, Any, Optional


class CryptographicAuthManifold:
    __slots__ = ("_global_salt", "_buffer_size", "_active_sessions")

    def __init__(self, global_salt: bytes = b"COREGRAPH_SOVEREIGN_SALT_001"):
        self._global_salt = global_salt
        self._buffer_size = 150 * 1024 * 1024
        self._active_sessions: Dict[bytes, float] = {}

    def verify_token_atomic(self, payload: bytes, provided_signature: bytes) -> bool:
        if len(provided_signature) != 64:
            return False
        expected_signature = (
            hmac.new(self._global_salt, payload, hashlib.sha256).hexdigest().encode("utf-8")
        )
        match = hmac.compare_digest(expected_signature, provided_signature)
        if match:
            self._active_sessions[provided_signature] = time.monotonic() + 3600.0
        return match

    def sweep_expired_sessions(self) -> None:
        current_time = time.monotonic()
        expired_keys = [k for k, v in self._active_sessions.items() if current_time > v]
        for k in expired_keys:
            del self._active_sessions[k]
