from backend.dal.utils.binary_encoder import BinaryEncoder
from backend.dal.utils.buffer_pool import BufferPool

class SerializationManifold:
    def __init__(self, capacity=4000000):
        # Enforcing fixed residency bounds: Capacity * 24 bytes
        self.pool = BufferPool(capacity * 24)
        self.capacity = capacity
        self.cursor = 0
        
    def serialize_batch(self, nodes):
        encoded_bytes = 0
        for node in nodes:
            BinaryEncoder.encode_node(self.pool.buffer, self.cursor, *node)
            self.cursor += 24
            encoded_bytes += 24
        return encoded_bytes
        
    def deserialize_node(self, index):
        return BinaryEncoder.decode_node(self.pool.buffer, index * 24)
