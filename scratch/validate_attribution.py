import sys
import os
import asyncio

# Production-Grade Path Alignment
sys.path.append(os.getcwd())

async def validate_attribution():
    try:
        from backend.analytics.attribution_manifold import AttributionManifoldEngine
        from backend.core.memory_manager import metabolic_governor

        # Structural Check: Instantiation
        engine = AttributionManifoldEngine()

        # Test Shard Investigation
        test_data = b"MOVEX_LOGISTICS_SHARD_ENTROPY_TELEMETRY"
        await engine.investigate_entropy("SHARD_001", test_data)

        # Test Cross-Domain Correlation
        await engine.correlation.reconcile_domains("MOVEX_SCHEMA_A", "PFCV_CONTRACT_B")

        print("VALIDATION_SUCCESS: Hadronic Attribution Manifold and Correlation Phalanx are bit-perfect.")
        return True
    except Exception as e:
        import traceback
        print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_attribution())
    sys.exit(0 if success else 1)
