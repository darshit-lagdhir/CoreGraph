import sys
import os
import asyncio

# Production-Grade Path Alignment
sys.path.append(os.getcwd())

async def validate_verification():
    try:
        from backend.analytics.verification_manifold import VerificationManifoldEngine
        from backend.persistence.persistent_vault_engine import PersistentVaultEngine

        # Structural Check: Instantiation
        vault = PersistentVaultEngine()
        engine = VerificationManifoldEngine(vault)

        # Test Integrity Scan
        success = await engine.kernel.execute_integrity_scan(b"CORE_SHARD_TELEMETRY")
        if not success:
            raise ValueError("Integrity Scan Failed.")

        # Test Trace Correlation
        engine.phalanx.register_trace("TRACE_001", "INGESTION")
        if not engine.phalanx.verify_trace("TRACE_001", "INGESTION"):
            raise ValueError("Trace Verification Failed.")

        print("VALIDATION_SUCCESS: Mission-Critical Verification Manifold and Audit Kernel are bit-perfect.")
        return True
    except Exception as e:
        import traceback
        print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_verification())
    sys.exit(0 if success else 1)
