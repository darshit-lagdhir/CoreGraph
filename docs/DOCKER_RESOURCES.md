# THE CONTAINER ARCHITECTURE AND VIRTUALIZED RESOURCE ISOLATION MANIFEST

## INTRODUCTION: THE VIRTUALIZED PERIMETER

Welcome to the **Container Architecture and Virtualized Resource Isolation**
architectural manifest.

The CoreGraph engine is designed to execute as a high-density intelligence cluster
within a containerized environment. To maintain the 150MB residency limit, the
underlying containerization layer must be tuned to provide absolute resource
guarantees.

By analyzing the `Dockerfile`, `docker-compose.yml`, and `redis.conf`, we establish
the definitive technical architecture defining virtualized sovereignty.

---

## SECTOR 1: MULTI-STAGE BUILD ARCHITECTURE AND IMAGE COMPRESSION

The CoreGraph `Dockerfile` implements a multi-stage build process to ensure the
final production image is as lean as possible.

- **Stage 1 (Building):** Compiles the C-extensions for the Hadronic core.
- **Stage 2 (Production):** Copies only the compiled binaries and necessary
  source code into a distroless or Alpine-based vacuum.

---

## SECTOR 2: THE COMPOSER MANIFOLD AND RESOURCE LIMITS

The `docker-compose.yml` file defines the strict limits for the engine's
physical execution.

```yaml
services:
  core-engine:
    image: coregraph-engine:latest
    deploy:
      resources:
        limits:
          memory: 200M
          cpus: '0.5'
```

By setting a 200M limit at the Docker level, the container provides a small safety
overhead for the internal 150MB MetabolicLimiter.

---

## SECTOR 3: POSTGRESQL AND REDIS SECURITY ISOLATION

The database and event bus layers are isolated within a private Docker bridge network.
This prevents external actors from interacting directly with the forensic data
layers.

---

## SECTOR 4: WSL2 HYPERVISOR BOUNDS

For operators running CoreGraph on Windows 11, the WSL2 environment must be
configured to prevent resource starvation.

```ini
[wsl2]
memory=16GB
processors=16
swap=0
localhostForwarding=true
```

Disabling swap natively (`swap=0`) prevents the host from paging memory to disk,
ensuring the system maintains high-speed asynchronous throughput by strictly
utilizing physical RAM.

If the limits are exceeded, disabling the WSL swap ensures the OOM killer reacts
instantaneously inside the container, instead of forcing the Windows host to page
gigabytes of memory onto physical hard drives.

---

## APPENDIX A: EXTENSIVE TOPOLOGICAL EXPANSION AND METRIC VERIFICATION MATRICES

This structural appendix provides explicit resolutions for errors resulting from
failure to adhere precisely to the constraints implemented inside the Core Engine's
virtualized boundary.
