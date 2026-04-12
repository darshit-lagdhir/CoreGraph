import struct


class MissionFidelityKernel:
    def evaluate_health_vector(self, telemetry: bytes) -> float:
        l = len(telemetry) // 8
        if l == 0:
            return 1.0
        floats = struct.unpack(f">{l}d", telemetry)
        return sum(floats) / l
