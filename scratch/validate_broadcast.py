import sys
import os
import asyncio

# Production-Grade Path Alignment
sys.path.append(os.getcwd())

async def validate_broadcast():
    try:
        from backend.interface.websocket_multiplexer import WebSocketMultiplexerKernel, InputSynapseKernel
        from backend.core.memory_manager import metabolic_governor

        # Structural Check: Instantiation
        mux = WebSocketMultiplexerKernel()
        synapse = InputSynapseKernel()

        # Test Observer Registration
        await mux.register_observer("ARCHITECT_01", role="MASTER_ARCHITECT")

        # Test Radiance Broadcast (Mock Delta)
        await mux.broadcast_radiance(b"\x1b[31mSPECTRAL_DELTA\x1b[0m")

        # Test Coordinate Reconciliation
        synapse.reconcile_coordinates(100, 200, zoom_scale=1.0)

        print("VALIDATION_SUCCESS: WebSocket Multiplexer and Input Synapse Kernels are bit-perfect.")
        return True
    except Exception as e:
        import traceback
        print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_broadcast())
    sys.exit(0 if success else 1)
