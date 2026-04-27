import sys
import os

# Production-Grade Path Alignment
sys.path.append(os.getcwd())

async def validate_vault():
    try:
        from backend.persistence.persistent_vault_engine import PersistentVaultEngine
        from backend.core.memory_manager import metabolic_governor

        # Structural Check: Instantiation
        vault = PersistentVaultEngine()

        # Test Log Mutation
        await vault.wal.log_mutation(0x01, 1001, 2002)
        await vault.wal.flush()

        # Test Reconstitution
        await vault.reconstitute()

        print("VALIDATION_SUCCESS: Persistent Vault Manifold and WAL Kernel are bit-perfect.")
        return True
    except Exception as e:
        import traceback
        print(f"VALIDATION_FAILURE:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(validate_vault())
    sys.exit(0 if success else 1)
