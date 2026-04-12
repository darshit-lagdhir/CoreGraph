import hashlib
class RelationalSarcophagus:
    def pack_dependency(self, parent: bytes, child: bytes) -> bytes:
        return parent + b'|' + child
    
    def sign_dependency(self, rel: bytes) -> bytes:
        return hashlib.blake2b(rel).digest()
