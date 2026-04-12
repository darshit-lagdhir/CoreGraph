import struct


class BinaryEncoder:
    @staticmethod
    def encode_node(buffer, offset, node_id, ts, x, y, risk):
        # Format: < = Little Endian, I = uint32, Q = uint64, f = float32 -> 24 bytes total
        struct.pack_into("<IQfff", buffer, offset, node_id, ts, x, y, risk)
        return 24

    @staticmethod
    def decode_node(buffer, offset):
        return struct.unpack_from("<IQfff", buffer, offset)
