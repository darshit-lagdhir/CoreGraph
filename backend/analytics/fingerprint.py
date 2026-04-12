import hashlib
import struct


class FingerprintKernel:
    @staticmethod
    def generate(namespace: str, name: str) -> int:
        h = hashlib.blake2b(f"{namespace}::{name}".encode("utf-8"), digest_size=8).digest()
        return struct.unpack("<Q", h)[0]
