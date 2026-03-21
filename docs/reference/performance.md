# CoreGraph Performance Boundary Log

This ledger documents the strict performance and latency guardrails derived from continuous hardware calibration against the 24-core i9-13980hx processor and 16GB total system memory.

## 1. Network and Storage Thresholds
- **PostgreSQL Connection Pool**: The asynchronous SQLAlchemy configuration must cap the connection pool to tightly bound limits, preventing socket exhaustion during bulk recursive ingestion operations.
- **WebSocket Telemetry Chunks**: The platform transmits binary representations of topological geometry. These packets are constrained to strictly chunked $64\text{KB}$ sizes to bypass buffer limits and are strictly compressed utilizing the `zlib` stream convention, which the client process must decompress via `pako`.

## 2. Rendering Physics Baseline
- **WebGL Frame Execution**: To handle the physics-driven attraction logic across the graphical canvas mapping 100,000+ localized active nodes, the fragment shaders must conclude their execution within an 8-millisecond loop threshold. This rigidly guarantees exactly 60 Frames Per Second (FPS) on the target RTX 4060 GPU to prevent cognitive strain on operators reading the threat map.
- **Node Caching Limits**: 12-hour TTLs ensure deterministic offloading and serialization for massive DAG graphs, averting cache stampedes over the Redis backbone.

For more specifics detailing the architectural boundaries enforced under WSL2, consult the `[Architecture Ledger](architecture.md)`.
