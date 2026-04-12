import hashlib


class StorageIntegrityVerifier:
    def verify_write(self, memory_block: bytes, signature: bytes) -> bool:
        return hashlib.blake2b(memory_block).digest() == signature
