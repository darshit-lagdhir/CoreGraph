import os
import time
import platform
import subprocess
from typing import Dict, Any, Optional

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

class HostSensingKernel:
    """
    Module 4 - Task 021: Host Sensing Kernel.
    Silicon-native scout detecting CPU topology, RAM residency, and I/O pacing.
    Governs the dynamic transition between Redline and Potato execution tiers.
    """
    __slots__ = (
        '_metrics',
        '_master_constants',
        '_mock_override',
        '_safety_margin'
    )

    _instance: Optional['HostSensingKernel'] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> 'HostSensingKernel':
        """Singleton Enforcer over Master Constants Array."""
        if cls._instance is None:
            cls._instance = super(HostSensingKernel, cls).__new__(cls)
        return cls._instance

    def __init__(self, mock_override: Optional[Dict[str, Any]] = None):
        if hasattr(self, '_metrics') and not mock_override:
            return

        self._mock_override = mock_override
        self._safety_margin = 0.70  # 70% Max RAM Allocation Ceiling
        self._metrics: Dict[str, Any] = {
            'c_phys': 1,
            'c_log': 1,
            'ram_total_gb': 1.0,
            'ram_avail_gb': 1.0,
            'io_speed_mbps': 50.0,
            'net_bandwidth_mbps': 10.0,
            'tier': 'POTATO',
            'score': 0.0
        }
        self._master_constants: Dict[str, Any] = {}

    def _scan_cpu_topology(self) -> None:
        if self._mock_override and 'cpu' in self._mock_override:
            self._metrics['c_phys'] = self._mock_override['cpu'].get('physical', 1)
            self._metrics['c_log'] = self._mock_override['cpu'].get('logical', 1)
            return

        if psutil:
            self._metrics['c_phys'] = psutil.cpu_count(logical=False) or 1
            self._metrics['c_log'] = psutil.cpu_count(logical=True) or 1
        else:
            self._metrics['c_phys'] = os.cpu_count() or 1
            self._metrics['c_log'] = self._metrics['c_phys']

    def _map_ram_residency(self) -> None:
        if self._mock_override and 'ram' in self._mock_override:
            self._metrics['ram_total_gb'] = self._mock_override['ram'].get('total', 1.0)
            self._metrics['ram_avail_gb'] = self._mock_override['ram'].get('available', 1.0)
            return

        if psutil:
            mem = psutil.virtual_memory()
            self._metrics['ram_total_gb'] = mem.total / (1024 ** 3)
            self._metrics['ram_avail_gb'] = mem.available / (1024 ** 3)
        else:
            # Fallback estimation for environments without psutil
            self._metrics['ram_total_gb'] = 4.0
            self._metrics['ram_avail_gb'] = 2.0

    def _benchmark_io_throughput(self) -> None:
        """
        Executes a rapid 4KB and 1MB non-destructive write matrix to calculate
        Sequential Throughput. Bypasses actual destructive benchmarks if mocked.
        """
        if self._mock_override and 'io' in self._mock_override:
            self._metrics['io_speed_mbps'] = self._mock_override['io']
            return

        test_file = ".coregraph_io_probe.tmp"
        try:
            start = time.time()
            data = b'0' * (1024 * 1024)  # 1MB block
            with open(test_file, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            duration = time.time() - start
            self._metrics['io_speed_mbps'] = 1.0 / max(duration, 0.001)
        except Exception:
            self._metrics['io_speed_mbps'] = 50.0  # Fallback SATA Mechanical
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def _probe_network_infrastructure(self) -> None:
        """Estimates downstream latency and available sockets (Mocked fast-path)."""
        if self._mock_override and 'network' in self._mock_override:
            self._metrics['net_bandwidth_mbps'] = self._mock_override['network']
            return

        # Fast synthetic approximation without saturating actual TCP sockets on boot
        self._metrics['net_bandwidth_mbps'] = 100.0

    def _calculate_hardware_tier(self) -> None:
        m = self._metrics
        
        score = (m['c_phys'] * 0.4) + (m['ram_avail_gb'] * 0.3) + (m['io_speed_mbps'] * 0.2) + (m['net_bandwidth_mbps'] * 0.1)
        m['score'] = score

        if score > 100:
            m['tier'] = 'REDLINE'
        elif score > 40:
            m['tier'] = 'MIDRANGE'
        else:
            m['tier'] = 'POTATO'

    def generate_master_constants(self) -> Dict[str, Any]:
        """
        Primary module entrypoint. Aggregates metrics and constructs the singleton
        Master Constants Table governing all phalanx behaviors.
        """
        self._scan_cpu_topology()
        self._map_ram_residency()
        self._benchmark_io_throughput()
        self._probe_network_infrastructure()
        self._calculate_hardware_tier()

        m = self._metrics
        tier = m['tier']
        
        # Base multiplier according to Engineering Specification 021
        if tier == 'REDLINE':
            density_multiplier = 2.5
            chunk_size = 10000
            mmap_size = 1024 * 1024 * 512  # 512MB
            telemetry_hz = 0.016  # 60Hz
            yield_threshold = 2000
        elif tier == 'MIDRANGE':
            density_multiplier = 1.5
            chunk_size = 2500
            mmap_size = 1024 * 1024 * 64   # 64MB
            telemetry_hz = 0.05   # 20Hz
            yield_threshold = 500
        else:
            density_multiplier = 0.5
            chunk_size = 250
            mmap_size = 1024 * 1024 * 16   # 16MB
            telemetry_hz = 0.2    # 5Hz
            yield_threshold = 50

        # Phalanx Equation
        max_registry_allowed = 100
        worker_count = max(1, min(max_registry_allowed, int(m['c_phys'] * density_multiplier)))

        self._master_constants = {
            'WORKER_COUNT': worker_count,
            'PERSISTENCE_CHUNK_SIZE': chunk_size,
            'MMAP_BUFFER_SIZE': mmap_size,
            'TELEMETRY_FREQUENCY': telemetry_hz,
            'PARSER_YIELD_THRESHOLD': yield_threshold,
            'HARDWARE_TIER': tier,
            'SYSTEM_SCORE': m['score'],
            'SAFE_HEAP_LIMIT_GB': m['ram_avail_gb'] * self._safety_margin
        }

        return self._master_constants

    def get_constants(self) -> Dict[str, Any]:
        if not self._master_constants:
            return self.generate_master_constants()
        return self._master_constants
