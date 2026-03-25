import os
import hashlib
from typing import Dict

class FinalSeal:
    """
    S.U.S.E. Final Repository Sealing (Task 025).
    The 'Guardian of the Seal' for the 3.84M node universe.
    """
    AUTHORIZED_DIRS = {"backend", "tooling", "infra", "frontend", "scripts", "docs"}
    SEAL_FILE = ".seal-include"
    
    @staticmethod
    def _get_hash(path: str) -> str:
        """
        SHA-256 for bit-for-bit cryptographic consistency.
        """
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def generate_manifest(self, root_dir: str):
        """
        Manifest Generation: Listing authorized files with SHA-256 hashes.
        """
        print("[SEAL] Generating Final Project Manifest (P-Core Accelerated)...")
        manifest: Dict[str, str] = {}
        for root, dirs, files in os.walk(root_dir):
            if any(forbidden in root for forbidden in [".git", "venv", ".workspace"]):
                continue
                
            rel_root = os.path.relpath(root, root_dir)
            if any(rel_root.startswith(d) for d in self.AUTHORIZED_DIRS) or rel_root == ".":
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, root_dir)
                    manifest[rel_path] = self._get_hash(full_path)

        with open(os.path.join(root_dir, self.SEAL_FILE), "w") as f:
            for path, hset in manifest.items():
                f.write(f"{path}:{hset}\n")
        print(f"[SUCCESS] Manifest Generated: {len(manifest)} files SEALED.")

if __name__ == "__main__":
    sealer = FinalSeal()
    sealer.generate_manifest(os.getcwd())
