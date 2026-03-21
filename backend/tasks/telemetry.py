import logging
import psutil
import subprocess
from worker import celery_app
from core.logging_config import correlation_id_var


@celery_app.task(name="telemetry.heartbeat")
def emit_hardware_telemetry():
    """Engine Heartbeat: Emits structure high-fidelity hardware traces into the OSINT matrix."""
    # 1. i9-13980hx Core Utilization Analysis
    cpu_percent = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()

    # 2. VRAM Observability for the RTX 4060 geometry shaders
    vram_used = 0
    try:
        # Utilizing NVIDIA's Management Interface for physical VRAM sampling
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            encoding="utf-8",
        )
        vram_used = int(output.strip())
    except Exception:
        # Fallback for headless CI or non-NVIDIA local simulation environments
        pass

    # Trace Emission utilizing structured JSON matrix
    logging.info(
        "SYSTEMIC_TELEMETRY_PULSE",
        extra={
            "cpu_total_percent": cpu_percent,
            "memory_available_gb": mem.available / (1024**3),
            "vram_used_mb": vram_used,
            "core_count": psutil.cpu_count(),
            "frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
        },
    )

    # 3. Memory Boundary Alerting (8GB wsl2 hypervisor leash)
    if mem.available < (1.0 * 1024**3):
        logging.critical(
            "HYPERVISOR_MEMORY_CRITICAL: Less than 1GB available RAM on workstation node."
        )

    if vram_used > 7000:
        logging.warning(
            "VRAM_LIMIT_THRESHOLD: RTX 4060 approaching 8GB threshold. Triggering LOD Downscaler."
        )
