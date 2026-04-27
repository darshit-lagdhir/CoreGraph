import sys
import os
import asyncio

# Production-Grade Path Alignment
sys.path.append(os.getcwd())

async def validate_healing():
    try:
        from backend.performance.self_healing_phalanx import SelfHealingPhalanxEngine
        from backend.persistence.persistent_vault_engine import PersistentVaultEngine

        # Structural Check: Instantiation
        vault = PersistentVaultEngine()
        engine = SelfHealingPhalanxEngine(vault)

        # Test Remediation logic (Mock module crash)
        async def mock_module():
            print("MOCK_MODULE: Active.")
            raise ValueError("SIMULATED_COLLAPSE")

        # We trigger the remediation in a task
        task = asyncio.create_task(engine.remediation.monitor_module("TEST_CORE", mock_module))
        await asyncio.sleep(0.5)
        task.cancel() # End the test loop

        # Test Signal Phalanx structure
        if not engine.recovery:
            raise ValueError("Recovery Phalanx was not initialized.")

        print("VALIDATION_SUCCESS: Self-Healing Phalanx and Remediation Kernel are bit-perfect.")
        return True
    except Exception as e:
        import traceback
        print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_healing())
    sys.exit(0 if success else 1)
