import hashlib


class BitwiseReconciler:
    def hash_state(self, payload: bytes) -> bytes:
        return hashlib.blake2b(payload).digest()

    def merge(self, current: bytes, incoming: bytes) -> bytes:
        return current if self.hash_state(current) == self.hash_state(incoming) else incoming
