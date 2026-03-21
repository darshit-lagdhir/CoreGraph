# CoreGraph Architectural Ledger

This document explicitly defines the physical mapping, network bounds, and execution topology of the CoreGraph distributed Open-Source Intelligence (OSINT) platform.

## 1. Hardware Utilization and Boundaries
The architecture is designed to exploit the physical capabilities of the reference workstation hardware without breaching strict hypervisor limits.
- **Processor**: Intel Core i9-13980hx (24 cores)
- **Graphical Hardware**: NVIDIA RTX 4060 GPU
- **System Memory Constraint**: 16GB Total RAM
- **WSL2 Hypervisor Leash**: Strictly bounded to 8GB to prevent resource starvation during complex WebGL context allocation in the browser. (Reference: `[Performance Guidelines](performance.md)`).

## 2. Distributed Execution Topology
The platform's compute workload is divided across several highly specialized container topologies running on a localized Bridge Network.
- **ASGI Gateway**: High-throughput FastAPI event loops executing under unprivileged contexts.
- **PostgreSQL Vault**: Bound to port 5433 (mapped from internal 5432) storing up to 3.88 million relational node structures.
- **Celery Orchestration Pool**: A 16-worker concurrent processing pool managing the ingestion primitives and memory-heavy structural serialization.

## 3. Quarantined Components
The documentation infrastructure is explicitly partitioned within `docs/reference/` and `docs/static/`. Business logic never resides within the root project tree.

For the mathematical algorithms governing the PageRank and Blast Radius calculations, consult the `[Algorithms Blueprint](algorithms.md)`.
