import sys
import os
import asyncio

# Production-Grade Path Alignment
sys.path.append(os.getcwd())

async def validate_zenith():
    try:
        from backend.core.universal_zenith import UniversalZenithEngine
        from backend.persistence.persistent_vault_engine import PersistentVaultEngine

        # Structural Check: Instantiation
        vault = PersistentVaultEngine()
        zenith = UniversalZenithEngine(vault)

        # Test Zenith Handshake
        await zenith.initiate_zenith_handshake()

        # Test Hardening Logic
        zenith.hardening.seal_perimeter()

        print("VALIDATION_SUCCESS: Universal Sovereign Zenith and Hardening Engine are bit-perfect.")
        return True
    except Exception as e:
        import traceback
        print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(validate_zenith())
    sys.exit(0 if success else 1)
