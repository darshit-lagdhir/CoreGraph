#!/bin/bash
# CoreGraph Hardware Bootstrapper
# Implements "Total Performance Paradigm" core-aware scheduling & sysctl tuning

echo "[INFO] Commencing Core-Aware Orchestration (i9-13980hx)"

# Enforce Transparent Huge Pages for PostgreSQL shared buffers
echo "madvise" > /sys/kernel/mm/transparent_hugepage/enabled
echo 512 > /proc/sys/vm/nr_hugepages

# Kernel TCP Window and Buffer Scaling (16MB buffers for WebSocket telemetry)
sysctl -w net.core.rmem_max=16777216
sysctl -w net.core.wmem_max=16777216
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
sysctl -w net.ipv4.tcp_slow_start_after_idle=0

# Hardware Affinity Guardrails using taskset and cgroups
# P-Core allocation (0-15) for ASGI Gateway and WebGL rendering (Core 0/1 exclusive lock)
# E-Core allocation (16-23) for Celery workers & telemetry

echo "[INFO] Spawning cgroups and assigning thread controllers"
mkdir -p /sys/fs/cgroup/cpuset/coregraph_frontend
mkdir -p /sys/fs/cgroup/cpuset/coregraph_backend_analytics
mkdir -p /sys/fs/cgroup/cpuset/coregraph_db

# Pin db to cores 0-3 (P-Cores)
echo "0-3" > /sys/fs/cgroup/cpuset/coregraph_db/cpuset.cpus
# Pin UI/ASGI to cores 0-1, 4-15 (P-Cores)
echo "0-1,4-15" > /sys/fs/cgroup/cpuset/coregraph_frontend/cpuset.cpus
# Pin Celery to cores 16-23 (E-cores)
echo "16-23" > /sys/fs/cgroup/cpuset/coregraph_backend_analytics/cpuset.cpus

# Set TGP to 140W and lock GPU clock to 2000MHz for NVIDIA RTX 4060
if command -v nvidia-smi &> /dev/null; then
    echo "[INFO] Locking RTX 4060 clock to 2000MHz to eliminate WebGL micro-stutter"
    nvidia-smi -lgc 2000
    nvidia-smi -pl 140
fi

echo "[INFO] Hardware Bootstrap Complete. Module 1 Sealed."
