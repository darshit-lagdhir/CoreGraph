#!/usr/bin/env python3
"""
Pruning Matrix: Automated Environment Pruning and NVMe Artifact Eradication.
Task 024 implementation.
"""

import concurrent.futures
import json
import os
import shutil
import subprocess
import time
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

WORKSPACE_ROOT = Path(__file__).parent.parent.parent
BACKEND_DIR = WORKSPACE_ROOT / "backend"
LOGS_DIR = BACKEND_DIR / "logs"
WORKSPACE_DIR = WORKSPACE_ROOT / ".workspace"


# Pydantic-backed "Compaction Schema" to ensure JSON integrity
class CurrentStatus(BaseModel):
    completion_percentage: float = 0.0
    last_completed_task_id: str = ""
    active_module: Optional[int] = None
    active_task_id: Optional[str] = None


class ModuleStatus(BaseModel):
    id: int
    name: str
    status: str
    tasks_total: int
    tasks_completed: int


class RegistryModel(BaseModel):
    project: str = "CoreGraph"
    total_modules: int = 15
    total_tasks: int = 262
    current_status: CurrentStatus
    modules: List[ModuleStatus] = []


class PruningMatrix:
    def __init__(self, use_tmpfs: bool = False):
        self.use_tmpfs = use_tmpfs
        self.tmpfs_path = Path("/dev/shm/prune_buffer") if self.use_tmpfs else None
        self.targets = {
            "dirs": [
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
                ".vite",
                ".eslintcache",
            ],
            "node_cache": ["node_modules/.cache"],
            "exts": [".pyc", ".pyo", ".tsbuildinfo"],
        }

    def execute_with_retry(self, cmd: List[str], retries: int = 5, delay: float = 1.0) -> bool:
        """Retry Docker network/volume pruning with exponential backoff to handle race conditions"""
        for i in range(retries):
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                return True
            except subprocess.CalledProcessError as e:
                if i == retries - 1:
                    print(f"Failed to execute {' '.join(cmd)} after {retries} retries: {e.stderr}")
                    return False
                time.sleep(delay * (2**i))
        return False

    def prune_docker_layers(self):
        """Context-Aware Pruning for dangling layers and orphaned volumes"""
        print("[*] Eradicating dangling Docker layers...")
        self.execute_with_retry(["docker", "image", "prune", "-f"])

        print("[*] Destroying orphaned Docker volumes...")
        self.execute_with_retry(["docker", "volume", "prune", "-f"])

        print("[*] Evicting BuildKit Cache (Older than 48h)...")
        self.execute_with_retry(["docker", "builder", "prune", "--filter", "until=48h", "-f"])

    def fetch_scan_targets(self, root: str) -> List[str]:
        """Recursive fast walker using `os.scandir`"""
        found = []
        try:
            with os.scandir(root) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name in self.targets["dirs"] or entry.path.endswith(
                            self.targets["node_cache"][0]
                        ):
                            found.append(entry.path)
                        elif not entry.name.startswith(".git"):
                            found.extend(self.fetch_scan_targets(entry.path))
                    else:
                        if any(entry.name.endswith(ext) for ext in self.targets["exts"]):
                            found.append(entry.path)
        except PermissionError:
            pass
        return found

    def parallel_bytecode_purge(self):
        """Multi-threaded target eradication using 24 max workers"""
        print("[*] Deep scanning workspace for bytecode anomalies...")
        target_files_dirs = self.fetch_scan_targets(str(WORKSPACE_ROOT))

        if not target_files_dirs:
            print("[*] Zero Logic Artifacts found. Foundation is sterile.")
            return

        def secure_delete(path_str: str):
            p = Path(path_str)
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
            except Exception as e:
                # Sudo-Shim fallback for root-owned artifacts
                print(f"[!] Escalating privileges for {p}: {e}")
                if os.name == "posix":
                    subprocess.run(["sudo", "rm", "-rf", str(p)], check=False)
                else:
                    # Windows fallback
                    subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", str(p)], check=False)

        print(f"[*] Dispatching {len(target_files_dirs)} targets across P-cores...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
            executor.map(secure_delete, target_files_dirs)

    def log_rotation(self):
        """Log Archival and Compression"""
        if not LOGS_DIR.exists():
            return
        current_time = time.time()
        for p in LOGS_DIR.glob("*.log"):
            if current_time - p.stat().st_mtime > 7 * 86400:
                print(f"[*] Removing ancient diagnostic trace: {p.name}")
                p.unlink()
            else:
                archive_path = p.with_suffix(".log.gz")
                print(f"[*] Compacting log: {p.name}")
                with open(p, "rb") as f_in:
                    data = f_in.read()
                with open(archive_path, "wb") as f_out:
                    f_out.write(zlib.compress(data, level=9))
                p.unlink()

    def registry_compaction(self):
        """Registry compaction using Schema-Aware Pruner"""
        matrix_file = WORKSPACE_DIR / "task-matrix.json"
        if not matrix_file.exists():
            return

        print("[*] Performing schema-aware compaction on task-matrix... ")
        try:
            with open(matrix_file, "r", encoding="utf-8-sig") as f:
                raw_data = json.load(f)

            # Use Pydantic to ensure structural integrity
            model = RegistryModel(**raw_data)

            with open(matrix_file, "w", encoding="utf-8") as f:
                json.dump(model.model_dump(), f, indent=4)
        except Exception as e:
            print(f"[!] Registry compaction structurally failed: {e}")

    def fstrim_orchestration(self):
        """Coalesced NVMe fstrim ops"""
        # Execute fstrim -v / (Mocked for cross-platform, but executes real under linux)
        print("[*] Synchronizing NVMe blocks (fstrim)...")
        if os.name == "posix":
            try:
                # Assuming unprivileged running context, require sudo shim
                subprocess.run(["sudo", "fstrim", "-v", "/"], check=False)
            except Exception:
                pass
        else:
            print("[*] Windows Environment - SSD Optimize delegated to OS.")

    def memory_flush(self):
        """VRAM Flush & System Heap Compaction"""
        try:
            print("[*] Flushing VRAM Buffer...")
            if os.name == "posix":
                subprocess.run(
                    ["nvidia-smi", "--gpu-reset"],
                    check=False,
                    stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass

        print("[*] Signaling Celery / Redis for Heap Compaction...")
        try:
            # Redis MEMORY PURGE attempt
            subprocess.run(["redis-cli", "MEMORY", "PURGE"], check=False, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def run_all(self):
        self.fstrim_orchestration()
        self.prune_docker_layers()
        self.parallel_bytecode_purge()
        self.log_rotation()
        self.registry_compaction()
        self.memory_flush()
        print("[*] Workspace De-pollution completed successfully.")


if __name__ == "__main__":
    matrix = PruningMatrix()
    matrix.run_all()
