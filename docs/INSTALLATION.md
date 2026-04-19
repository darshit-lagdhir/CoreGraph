# THE INSTALLATION AND ENVIRONMENTAL SOVEREIGNTY: IGNITION MANIFEST

## INTRODUCTION: THE SYSTEMIC IGNITION OF THE TITAN

Welcome to the **Installation and Environmental Sovereignty Core**, explicitly
documented within this `INSTALLATION.md` absolute architectural manifest.

The CoreGraph Titan requires extreme hardware parameters to successfully deploy
its intelligence mappings. Initiating a planetary-scale OSINT engine across
consumer hardware represents a massive physical engineering hurdle.

The operating system environment must be tuned with absolute precision to manage
three million discrete graph nodes efficiently within a rigid 150MB residency
limit.

If a traditional deployment stack relies on standard background process models,
the Linux Kernel "Out Of Memory" (OOM) killer will inevitably obliterate the
process memory mapping within milliseconds of initial ingestion. This document
provides the explicit physics required to bridge the host operating system directly
into the CoreGraph asynchronous Python matrices.

A forensic intelligence tool installed incorrectly behaves fundamentally like
a compromised data sensor. If the underlying CPython engine cannot properly access
the physical storage controllers or network bridging sockets, the resulting OSINT
graphs will stutter, fail, and misrepresent analytical reality.

This is structurally unacceptable for industrial-grade certification.

This manual dictates the strict deployment routines required for mapping host
parameters organically. By following this architecture, the analyst constructs
an impermeable, frictionless vacuum inside which the Hadronic Sharding Kernel
can execute continuously.

---

## SECTOR 1: PRE-IGNITION HARDWARE SYNC VECTORS

Before executing any binary installations, you must structurally audit the
deploying hardware limits. Software performance represents a mathematical
subset of underlying physical constraint capabilities.

### 1.1 The Minimum Structural Hardware Requirements

The system demands physical architectures capable of handling immense random IOPS
bursts natively. To fully visualize the 144Hz Head-Up Display (HUD) cleanly
across an interactive terminal, the CPU must possess robust single-core metrics.

**Target Execution Sandbox (Laptop Class - ASUS ROG Strix G16 Equivalent):**
- **Processor Node:** Intel Core i9-13980HX or similar 24-core equivalent natively.
  The BORE (Burst-Oriented Response Enhancer) scheduler specifically utilizes the
  high-clocked Performance Cores (P-Cores) to manage the main asyncio event loop,
  while the Efficiency Cores (E-Cores) absorb the heavy disk I/O flushes. \\
- **Random Access Storage:** Minimum 32GB DDR5 5600MHz strongly enforced. While
  the container absolutely bounds itself explicitly to 150MB, the underlying host
  operating system requires clean RAM to aggressively buffer the massive
  continuous Write-Ahead Log streams coming from the PostgreSQL instance. \\
- **Physical Block Storage:** NVMe PCIe Gen4 M.2 Solid State Drive required.
  Utilizing slower magnetic SATA drives causes immediate Critical Commit Slope
  (CCS) saturation. Magnetic platters physically cannot align and flush 10,000
  sub-atomic binary tuples within the required 500-millisecond heartbeat.

### 1.2 The Sovereign Dual-Boot Environment

Deploying a high-speed engine natively against standard Windows Kernels introduces
unacceptable network subsystem delays via the translation layer. The Titan
operates optimally inside a native Unix topology.

**Garuda Linux Execution (Bare-Metal Sovereignty):**
If executing via dual-boot architectures, ensure the `linux-zen` kernel is
explicitly active. The Zen kernel patches dynamically re-tune the task scheduler,
favoring low-latency interactivity over server-grade batch processing throughput.
This strictly handles the rapid context-switching required between the UI HUD and
background disk workers perfectly.

**WSL2 Execution (Virtualized Windows Isolation):**
If constrained within a corporate Windows architecture, the system mandates the
activation of the Windows Subsystem for Linux (Version 2).

You must manually provision the global `.wslconfig` safely inside your home
directory (e.g. `C:\Users\Trojan\.wslconfig`).

```ini
[wsl2]
memory=16GB
processors=16
kernelCommandLine=sysctl.vm.max_map_count=524288
swap=0
```
This specific boundary optimally ensures the WSL2 hypervisor does not brutally
starve the host operating system of resources.

The `max_map_count` modification allows PostgreSQL's internal database workers
to allocate massive continuous Virtual Memory grids correctly for index scanning,
preventing fatal database crashes during heavy load.

Setting `swap=0` is critical. If the Linux subsystem exhausts its physical memory,
falling back to a dynamic Windows paging file (`pagefile.sys`) introduces massive
I/O blocking that will immediately destroy the 144Hz screen refresh rate. We
want the system to aggressively Out-Of-Memory (OOM) terminate processes rather
than smoothly degraded into unusable magnetic paging states.

---

## SECTOR 2: THE PYTHON VACUUM TUBE ISOLATION

Modern Python environments frequently suffer from catastrophic dependency
collisions. Installing libraries globally using system-level administrators
risks breaking native OS utilities that depend on standard package versions.

Executing the CoreGraph dependency tree correctly requires creating an absolute,
air-tight Python Virtual Machine envelope (the Vacuum Tube), isolating the OSINT
daemon physically from all external libraries.

### 2.1 Pyenv and Local Compiler Chains

The operator must configure `pyenv` to compile the specific Python 3.13 baseline
directly from C source blocks natively. Using system repositories (like `apt` or
`pacman`) leads to shared libraries that conflict with CoreGraph's asynchronous
C-extensions.

```bash
curl https://pyenv.run | bash

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pyenv install 3.13.0
pyenv local 3.13.0
```

By explicitly mapping structural boundaries locally, the operator controls the
C-compiler flags during the build process. Explicit `-O3` compilation flags
significantly enhance the underlying bytecode evaluation speed across the
internal event loops natively.

### 2.2 The Isolated Virtual Environment Genesis

Once the exact Python 3.13 bytecode interpreter is compiled and available in
the local path, the system dictates the creation of absolute physical isolation
utilizing the built-in `venv` module.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

Activating this environment intercepts the global `$PATH` variable on the local
kernel. When the analyst triggers the `pip install -r requirements.txt` command,
the site-packages are deposited exclusively inside the `.venv/` subdirectory.

This enables the operator to ruthlessly delete the entire physical environment by
simply issuing `rm -rf .venv/` if a dependency collision occurs during an upgrade,
establishing an easily reproducible, zero-contamination operational baseline.

---

## SECTOR 3: INFRASTRUCTURE CONFIGURATION AND CONTAINER GENESIS

While executing the Python code locally provides maximum development speeds for
architects, deploying the system for actual intelligence processing demands Docker
Containerization.

Docker encapsulates PostgreSQL, Redis, and the Python application inside a unified
software-defined network, perfectly imitating a production cloud orchestration.

### 3.1 Establishing Environment Variables

Before ignition, the deployment requires secrets. To safely handle cryptographic
keys, API tokens, and operational flags, the system relies on physical `.env`
injection rather than hard-coding values into the Python arrays.

Create explicitly the `.env.deploy` file in the repository root:

```ini
# Database Core Keys
POSTGRES_USER=titan
POSTGRES_PASSWORD=sovereign_str_key_99
POSTGRES_DB=coregraph_prod

# High Speed Event Bus
REDIS_URL=redis://redis-stream:6379/0

# Intelligence Networking
GITHUB_GRAPHQL_TOKEN=ghp_your_secure_token_here
GOOGLE_AI_API_KEY=AIza_your_secure_gemini_key

# Hardware Tunings
API_PORT=8000
ENVIRONMENT=production
LIMITER_MEGABYTES=150.0
```

These configuration vectors dictate how correctly the engine performs. The Python
layers utilize `os.environ.get()` directly. If `GITHUB_GRAPHQL_TOKEN` is missing,
the application explicitly refuses to initialize, rejecting the boot sequence
entirely rather than launching a broken graph analyzer silently.

### 3.2 Executing The Core Assembly

The CoreGraph engine utilizes a specialized `docker-compose.yml` file mapping
physical relationships and dependency boot orders natively.

```bash
docker-compose --env-file .env.deploy up -d --build
```

This single command triggers the execution cascade:
1. Docker evaluates the `Dockerfile` inside a multi-stage builder layer.
2. It compiles all Python memory structures into `.whl` files.
3. It initializes a clean Alpine Linux container, copying exclusively the required
   binary wheels.
4. It initializes PostgreSQL and Redis concurrently, utilizing Healthchecks to
   block further steps until the databases acknowledge they are ready to accept
   connections natively.
5. It mounts the new Python execution container onto a private software network
   bridge, booting the primary `main.py` entrypoint specifically restricted
   beneath specific Control Groups (cgroups) defining a 200MB physical memory bound.

---

## APPENDIX A: EXTENSIVE TOPOLOGICAL EXPANSION MATRICES

This structural appendix provides explicit resolutions for errors resulting from
failure to adhere to the rigid installation bounds mandated by the Titan platform.

### Archetype 1: Container Post-Boot Premature Exits (Code 137)
**Symptom:**
The administrator runs `docker-compose up`, but the `coregraph-engine` container
immediately halts, generating an Exit Code 137 inside the Docker logs without
printing an explicit Python error stacktrace.

**Resolution:**
Exit Code 137 translates specifically to the Docker Daemon invoking an absolute
SIGKILL against the container due to Memory Limit Saturation. The container attempted
to instantly allocate more physical memory upon boot than the bounds defined in the
deployment `resources` limits.

Ensure that your `LIMITER_MEGABYTES` variable in `.env.deploy` is properly
set to `150.0`. If a stale configuration pushes the internal application loop
to demand 500MB while the outer Docker cgroup restricts it to 200MB, Docker
will immediately and correctly violently execute the process completely.

### Archetype 2: PostgreSQL Binding Rejections
**Symptom:**
The application crashes natively upon the first operation loop, displaying a
critical failure regarding `psycopg2.OperationalError: FATAL: password
authentication failed for user "titan"`.

**Resolution:**
Your active `.env.deploy` file was modified AFTER the PostgreSQL initialization
ran. PostgreSQL only evaluates the `POSTGRES_PASSWORD` environment variable
on its very first physical boot initializing the data blocks perfectly safely.

If you changed the password later, the container retains the data blocks via
Docker Volumes. You must execute `docker-compose down -v` to aggressively
purge the internal volumes physically from the disk, ensuring the subsequent
restart runs the genesis initialization sequence correctly with the new strings.
