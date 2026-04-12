import struct
from backend.analytics.fingerprint import FingerprintKernel
class LinkageManifold:
    def __init__(self, max_entities=3810000):
        self.max_entities = max_entities
        self.table_size = max_entities * 2
        self.pool = bytearray(self.table_size * 12)
        self.entity_count = 0
    def resolve_entity(self, namespace: str, name: str) -> int:
        fp = FingerprintKernel.generate(namespace, name)
        idx = fp % self.table_size
        for _ in range(500):
            offset = idx * 12
            stored_fp, stored_id = struct.unpack_from('<QI', self.pool, offset)
            if stored_fp == 0:
                if self.entity_count >= self.max_entities:
                    raise OverflowError('IdentityOverflow')
                new_id = self.entity_count + 1
                struct.pack_into('<QI', self.pool, offset, fp, new_id)
                self.entity_count += 1
                return new_id
            elif stored_fp == fp:
                return stored_id
            idx = (idx + 1) % self.table_size
        raise OverflowError('LinkageBoundaryBreached')
