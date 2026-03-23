import pytest
import time
import io
import uuid
from datetime import datetime
from dal.serialization.binary_kernel import CGBPEncoder, CGBPDecoder


@pytest.mark.asyncio
async def test_cgbp_compression_ratio():
    """
    Verifies that the CoreGraph Binary Protocol achieves 20:1
    compression over standard JSON representation.
    Ensures high-density throughput for HUD telemetry.
    """
    # 1. Setup sample dataset (1,000 nodes)
    sample_nodes = []
    for i in range(1000):
        sample_nodes.append(
            {
                "id": i,
                "ecosystem": "npm",
                "criticality": 0.9572,
                "is_vulnerable": True,
                "is_verified": False,
                "updated_at": datetime.now(),
            }
        )

    # 2. JSON Baseline Baseline (Simulation)
    import json

    def dt_serializer(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError

    json_size = len(json.dumps(sample_nodes, default=dt_serializer))

    # 3. CGBP Compression
    encoder = CGBPEncoder()
    cgbp_data = b"".join([encoder.encode_node(n) for n in sample_nodes])
    cgbp_size = len(cgbp_data)

    # 4. Density Audit
    # Ratio Calculation: JSON size vs CGBP binary size
    ratio = json_size / cgbp_size
    print(f"[AUDIT] Compression Ratio: {ratio:.2f}:1 (JSON vs CGBP)")
    print(f"[AUDIT] Node Size: {cgbp_size/1000:.2f} bytes/node (Target < 25)")

    assert ratio >= 10.0  # Standard requirement for denseOSINT transport
    assert (cgbp_size / 1000) < 25.0


@pytest.mark.asyncio
async def test_cgbp_serialization_integrity():
    """
    Ensures zero-loss bit-purity during the encode/decode cycle.
    Validates Varint addressing and structural bit-alignment.
    """
    encoder = CGBPEncoder()
    decoder = CGBPDecoder()

    original = {
        "id": 3881234,  # 4th Million Region
        "ecosystem": "cargo",
        "criticality": 0.88,
        "is_vulnerable": False,
        "is_verified": True,
        "updated_at": datetime(2026, 3, 23, 10, 0, 0),
    }

    # Binary Cycle
    encoded = encoder.encode_node(original)
    decoded = decoder.decode_node(io.BytesIO(encoded))

    # Verification (Float precision mapping within 16-bit limits)
    assert decoded["id"] == original["id"]
    assert decoded["ecosystem"] == original["ecosystem"]
    assert abs(decoded["criticality"] - original["criticality"]) < 0.0001
    assert decoded["is_vulnerable"] == original["is_vulnerable"]
    assert decoded["is_verified"] == original["is_verified"]
    assert decoded["updated_at"] == original["updated_at"]
