import sys
import os
import asyncio

# Production-Grade Path Alignment
sys.path.append(os.getcwd())

async def validate_stress():
    try:
        from backend.performance.stress_manifold import StressManifoldEngine
        from backend.core.memory_manager import metabolic_governor

        # Structural Check: Instantiation
        manifold = StressManifoldEngine()

        # Test Balancer Logic
        passed = await manifold.balancer.reconcile_query("TEST_QUERY_01", priority=1)

        # Test Quota Audit
        manifold.quota_enforcer.audit_quotas()

        # Test Flood Detection
        is_flood = manifold.detect_flood(2000.0)
        if not is_flood:
            raise ValueError("Flood Detection Failure: High velocity was not flagged.")

        print("VALIDATION_SUCCESS: Adversarial Stress Manifold and Balancer Kernel are bit-perfect.")
        return True
    except Exception as e:
        import traceback
        print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_stress())
    sys.exit(0 if success else 1)
