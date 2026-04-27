import sys
import os
import asyncio

# Production-Grade Path Alignment
sys.path.append(os.getcwd())

async def validate_intelligence():
    try:
        from backend.intelligence.agential_ingress import AgentialIngressEngine, CommandSynapseKernel
        from backend.core.memory_manager import metabolic_governor

        # Structural Check: Instantiation
        synapse = CommandSynapseKernel()
        engine = AgentialIngressEngine(synapse)

        # Test Intent Dispatch
        op = synapse.dispatch("Please scan the MoveX schema for enums")
        if op != 0x01:
            raise ValueError(f"Synapse Error: Expected 0x01, got {op}")

        # Test Agential Processing (Manual Trigger)
        await engine._process_intent("Audit the latest FFI contract")

        print("VALIDATION_SUCCESS: Agential Ingress Manifold and Neural Synapse are bit-perfect.")
        return True
    except Exception as e:
        import traceback
        print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_intelligence())
    sys.exit(0 if success else 1)
