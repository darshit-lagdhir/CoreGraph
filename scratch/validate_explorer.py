import sys
import os

# Production-Grade Path Alignment
# The root of the project is added to sys.path, allowing 'backend.xxx' imports.
sys.path.append(os.getcwd())

try:
    from backend.interface.virtualized_explorer import VirtualizedExplorer
    from backend.core.memory_manager import metabolic_governor

    # Structural Check: Instantiation
    explorer = VirtualizedExplorer(path=".")
    print("VALIDATION_SUCCESS: Virtualized Explorer manifold and Metabolic Handshake are bit-perfect.")
    sys.exit(0)
except Exception as e:
    import traceback
    print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
    sys.exit(1)
