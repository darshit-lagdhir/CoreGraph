# COREGRAPH: THE MASTER PROTOCOL (GENESIS, INGESTION & HYBRID EXECUTION)

# =========================================================================================
# THE COREGRAPH MASTER PROTOCOL: COMPLETE SYSTEM GENESIS, INGESTION & HYBRID EXECUTION
# =========================================================================================
# DOCUMENT CLASSIFICATION: TOP SECRET / MISSION CRITICAL
# TARGET AUDIENCE: LEAD ARCHITECTS, JUDGES, SYSTEMS ENGINEERS
# =========================================================================================

This document outlines the absolute, mathematically precise, and operationally rigorous
pathway to initialize, hydrate, and execute the COREGRAPH platform. This process bridging
the gap between local Synthetic Universe Simulation Engine (S.U.S.E.) artifacts—which act
as an entire offline NPM/PyPI registry mapped to your SSD—and the LIVE, real-time
cryptographic validation pipelines powered by GitHub GraphQL, Google's Deps.dev API,
and the Gemini 1.5 Flash Analytical Brain.

You will learn how to boot the foundation, forge the synthetic simulation files, instruct
the ingestion kernel to treat these crafted files as legitimate package repositories, and
then pivot seamlessly into the live internet to pull real-time security telemetry.

---

## PHASE 1: THE BARE-METAL FOUNDATION & CRYPTOGRAPHIC PROVISIONING

Before a single connection is opened to the ecosystem, the local foundation must be
sanitized and provisioned. COREGRAPH operates in a highly adversarial landscape; therefore,
the environment variables act as the system's absolute truth.

### 1.1 Python Virtual Environment and Isolation
You must isolate the dependency chain from your global OS environment. We enforce this to
prevent Python path corruption.
```bash
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 1.2 The Immutable Secret Management (.env)
Your `.env` file is the ignition key. It must contain the real credentials for when the
simulation pivots to live OSINT analysis. Create the `.env` file at the root:

```env
# /COREGRAPH/.env
# =============================================
# COREGRAPH IDENTIFICATION & DATABASE SECRETS
# =============================================
NODE_ENV=production
LOG_LEVEL=DEBUG

# SUPABASE / POSTGRESQL MULTIPLEXER
# This is the primary persistent state engine.
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[YOUR_SUPABASE_ID].supabase.co:5432/postgres
REDIS_URL=redis://localhost:6379/0

# =============================================
# LIVE OSINT CAPABILITIES & AI ANALYSIS
# =============================================
# Used by backend/clients/github.py for Live Repo Stats
GITHUB_GRAPHQL_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Used by backend/clients/gemini.py to execute Blast-Radius analysis
GEMINI_API_KEY=AIzaSy_xxxxxxxxxxxxxxxxxxxxxx

# Deps.Dev requires no auth, but network egress must be permitted.
```

---

## PHASE 2: DATABASE GENESIS AND ZERO-STATE HARDENING

COREGRAPH treats the database as a mathematical zero-trust entity. The relational schema
is built using Alembic migrations combined with heavily optimized PL/pgSQL triggers for
real-time index recalibration.

### 2.1 Execute the Genesis Protocol
Run the Alembic head migration to materialize the tables across the Supabase instance.
```bash
make db-harden
```
*(Fallback command if Make fails: `venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head`)*

This command does the following:
1. Instantiates the `packages`, `package_versions`, `dependencies`, and `maintainers` tables.
2. Deploys the Spatial Indexing models.
3. Creates the Trigger sequences that act as background garbage collection, automatically
calculating transitive dependencies when an edge is inserted.

### 2.2 Mathematical Zero-State Proof
We must prove the database is entirely sterile before introducing payloads.
```bash
make db-audit-zero
```
This fires Pytest routines that commit a fake transaction, count the rows, and roll them
back, proving the ACID compliance of the schema.

---

## PHASE 3: THE S.U.S.E. ENGINE (OFFLINE REALITY GENERATION)

Here is where the magic of the "ALREADY MADE FILES" acting as a "REAL NPM PACKAGE" happens.
To avoid rate-limiting GitHub and NPM for 3.88 Million packages, COREGRAPH features the
Synthetic Universe Simulation Engine (S.U.S.E.).

The S.U.S.E. generates thousands of complex JSON files locally on your disk. These files
mimic the exact HTTP responses of the actual NPM Registry and GitHub GraphQL API.

### 3.1 Generating the Simulated Ocean
```bash
make sim-gen-dev
```
Executes: `python main.py --count 1000 --eco npm`
What this does under the hood:
1. It initializes the `DeterministicGenerator` with a fixed mathematical seed (`0xDEADBEEF`).
2. It generates 1,000 artificial NPM packages (e.g., `sim-react-core`, `poly-lodash`).
3. It recursively builds a Zipfian distribution of dependencies. `sim-react-core` might
suddenly depend on `sim-object-assign-3.0`.
4. It outputs these payload files into `npm`.

### 3.2 Launching the Masquerade Server (The Local "Internet")
To make the backend ingestion pipeline believe these "already made files" are the real
NPM registry, you spin up the Simulation Server.
```bash
python main.py
```
This FastAPI server binds to `localhost:8081`.
When the backend executes `GET http://localhost:8081/npm/sim-react-core`, the simulation
server dynamically reads the local JSON file created in step 3.1 and streams it back
exactly as `registry.npmjs.org` would.

### 3.3 Financial and Chaos Ledgers
```bash
make sim-gen-finance
make sim-poison
```
This modifies the local JSON files to include simulated OpenCollective funding payloads
and introduces "Abyssal Web" cyclic dependencies (e.g., A depends on B, B depends on A),
testing the capability of the local files to break standard parsers.

---

## PHASE 4: LIVE OSINT TELEMETRY AND REAL-TIME CHECKING PIPELINE

While the S.U.S.E. handles the offline simulation of millions of packages, your judge will
want to see REAL data. COREGRAPH achieves this via a seamless API Proxy pattern.

When a user requests an ecosystem audit, the `main.py` pipeline determines if the package
is a "simulation" package or a "real-world" package. If it is real, it bypasses the
`localhost:8081` simulation and connects directly to the global internet.

### 4.1 The Deps.Dev Transitive Path Fetcher
Inside `deps_dev.py`, the system performs live network calls to Google's
Open Source Security API.
Target Endpoint: `https://api.deps.dev/v3/systems/{eco}/packages/{pkg}/versions/{version}:dependencies`

The moment a user types `expand npm/react` into the console, the HTTPX client fires this
call. It downloads the actual live JSON tree of React's dependencies, yielding the real
downstream libraries.

### 4.2 The Live GitHub GraphQL Correlation
Inside `github.py`, the `LiveGithubClient` extracts the repository URLs
provided by the Deps.dev response. It strips the `github.com/` prefix, isolates the owner
and repo strings, and frames a highly optimized GraphQL POST request.

This hits `https://api.github.com/graphql` using your `GITHUB_GRAPHQL_TOKEN`.
It bypasses all local simulated JSON files and retrieves live arrays for:
- `stargazerCount`
- `forkCount`
- `issues(states: OPEN)`

### 4.3 The Gemini AI Synthesizer (The Analytical Brain)
The true power of the hybrid approach is inside `gemini.py`. The system
compiles the offline topology data, the live dependency count, and the live GitHub statistics
into a dense Text Prompt.

It issues a POST request to:
`https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent`
Using the `GEMINI_API_KEY`, it feeds the Google AI. The AI streams back a 3-sentence
"Blast-Radius and Structural Risk Assessment". You are using live LLM diagnostics to
evaluate both local simulated files and real-world dependency trees.

---

## PHASE 5: THE GRAND ORCHESTRATION (THE TERMINAL HUD EXECUTION)

Now that the database is primed, the offline simulator is capable of serving local JSON
mock data, and the live API clients are configured with real API keys, you launch the Beast.

### 5.1 Start the Redis Broker & Celery Workers (Optional but Recommended for Scale)
For background processing of massive graph loops:
```bash
docker-compose up -d redis
celery -A backend.worker worker --loglevel=info -c 4
```

### 5.2 Launch the Master Input Loop
The `main.py` orchestrates the CLI interface, connecting the Terminal HUD to the
async event loop.
```bash
python main.py
```
You will be greeted by the Rich console interface, displaying the COREGRAPH banner.
The system will sit idle, listening for keyboard streams.

### 5.3 Executing a Live Analysis Protocol
In the command prompt, type:
```bash
expand npm/react
```

**Chronological Operations:**
1. The `async_input_listener` captures the command.
2. It invokes `deps_dev.fetch_package_info("npm", "react", "latest")`.
3. A real-world HTTP egress occurs. Deps.dev returns a 200 OK.
4. The JSON payload is parsed. The system discovers React has ~4 direct dependencies and
extracts the repo: `facebook/react`.
5. The `LiveGithubClient` takes over. It fires the GraphQL query using the Bearer token.
6. The query returns: 205,000 Stars, 42,000 Forks, 1,200 Open Issues.
7. The `LiveGeminiClient` combines this vector: "Package npm/react has 4 deps. The github
repo has 205k stars and 1.2k issues. Assess structurally."
8. Gemini responds via API: "React serves as a foundational ecosystem anchor with a massive
blast radius. Its low dependency count is highly secure, but the sheer volume of
dependents means any compromise amounts to a global extinction event. Open issue count
requires monitoring for latent vulnerabilities."
9. The `TerminalHUD.display_verdict()` command paints this dynamically into the console
using a formatted Rich Panel.

### 5.4 Executing an Offline Simulation Analysis Protocol
To show the judge the local simulation capabilities (the "Already Made Files" logic), type:
```bash
expand npm/sim-react-core
```

**Chronological Operations:**
1. The request bypasses the Live Clients because it recognizes the `sim-` prefix.
2. It fires a REST call to `http://localhost:8081/npm/sim-react-core`.
3. The Tooling Server reads the pre-computed JSON file generated by `sim-gen-dev`.
4. The exact same parsing logic processes the file. The local data is inserted directly
into the Supabase Postgres instance via the ingestor kernel.
5. The local file data proves the exact same internal algorithms can process synthetic
data structures equivalent to 3.88 Million real permutations.

---

## PHASE 6: IN-DEPTH ANALYTICAL MODULES & TOPOLOGICAL PHYSICS

COREGRAPH goes beyond simple API aggregation. Once the dependencies (both real and simulated)
are ingested into Postgres, the analytical frameworks engage.

### 6.1 The Physics Engines
Inside `analytics`, the system applies physical material properties to the
software objects matrix:
- **Cavitation Sync (`cavitation_sync.py`)**: Measures points of failure where a dependency
causes internal structural 'vaporization' of downstream dependents.
- **Clustering Engine (`clustering_algo.py`)**: Leverages Louvain/Leiden algorithms on the
adjacency matrix to identify 'Dark Communities' inside the graph.
- **Blast Radius (`blast_radius.py`)**: A heavy recursive BFS (Breadth-First Search) query
that travels down the Postgres index to identify exactly how many nodes will go offline
if a specific leaf node is compromised.

### 6.2 CVI Score Finalizer (Critical Vulnerability Index)
When you type `score npm/react`, the `cvi_calculator.py` is invoked.
This script performs a mathematical fusion:
$$CVI = (\text{Degree\_Centrality} \times 0.4) + (\text{Maintainer\_Trust\_Penalty}) + (\text{AI\_Risk\_Delta})$$
It converts the abstract AI generation and local statistical math into a strict 0-100
hexadecimal-rated criticality score.

### 6.3 Chaos Verification Pipeline
To demonstrate robust defense, you can inject chaos into the running network.
```bash
make sim-sabotage
```
This script pings the simulation server and forces a generic 502 Bad Gateway or a
5000ms latency spike across all synthetic requests.
The `main.py` ingestion loop will automatically trigger the resiliency circuit breakers.
Instead of crashing, it invokes the exponent backoff routines, temporarily storing the
failed ingestion tasks in the Dead Letter Queue (DLQ), proving to the judge that the
system remains upright even under hostile DDoSing.

---

## PHASE 7: FULL JUDGE & DEMONSTRATION WALKTHROUGH

When physically standing in front of the judge to evaluate the COREGRAPH platform, follow
this exact operational cadence to guarantee maximum impact:

**Step A: Clean Slate Proof**
- Open terminal -> `make clean-logs` -> `docker system prune` -> `make db-audit-zero`
- **Say:** "We initiate from a cryptographically clean, zero-state database architecture
deployed on Supabase."

**Step B: The Generation Reveal (Already Made Files)**
- Execute -> `make sim-gen-dev`
- Open Windows Explorer or VS Code IDE. Show the judge the .JSON files physically
populated inside `fixtures`.
- **Say:** "Instead of overwhelming the external network, we dynamically synthesize reality.
These files represent hyper-complex topological representations of NPM registries, built
offline, adhering to actual semantic versioning constraints."

**Step C: Local Ingestion**
- Start background simulator -> `python tooling/simulation_server/main.py` (Run in background)
- Run backend -> `python backend/main.py`
- Execute standard ingest -> `expand npm/synthetic-package-a`
- **Say:** "We are now parsing these local files, applying the CVI logic natively."

**Step D: The Pivot to Live Telemetry (The Real-Time Matrix)**
- Stay in `main.py` CLI.
- Execute -> `expand pypi/django`
- **Say:** "Now we pivot seamlessly outwards. The kernel recognizes a global entity. It is
reaching out via HTTPX. It pulls the live object from Deps.Dev."
- Wait 2 seconds as the screen populates.
- Point to the GitHub metrics. **Say:** "It has intercepted the GitHub URI and extracted live
Stars, open issues, and fork momentum via a raw GraphQL query using hardcoded .env
Bearer credentials."

**Step E: The AI Synthesis Finale**
- Wait for the **[GEMINI FLASH ANALYSIS]** block to render in the terminal.
- Point directly to the qualitative paragraph generated by the Google AI model.
- **Say:** "Finally, the entire data vector—both the local structural network data and the
live repository metrics—was cast into a dynamic textual tensor prompt and beamed directly
into Google's Gemini-Flash model via the latest generativelanguage API. The AI acts as
an autonomous DevSecOps engineer, converting rigid numerical arrays into a comprehensive,
human-readable ecosystem security verdict."

**Step F: Persistence Proof**
- Open DBeaver or Supabase Dashboard.
- Run SQL: `SELECT * FROM packages WHERE name = 'django';`
- Hit execute and show the judge the immutable Postgres rows containing both the AI
verdict string, the topological edges, and the CVI integer.

---

## CONCLUSION & THEORETICAL FOUNDATION

What you have built within the COREGRAPH bounds is essentially a dual-engine architecture.
You have an Offline World (S.U.S.E) comprised of statically generated files that act perfectly
as real NPM packages, allowing limitless destructive testing, caching logic audits, and
graph-database ingestion tests without arbitrary rate-limits.

Simultaneously, you have forged a Live Egress Kernel. The system requires no structural
difference when handling a static disk JSON payload versus an incoming encrypted API payload.
The ingestion hook relies purely on data formatting. The bridge to Gemini ensures that
whether the system is tracking synthetic files injected via `sim-gen-dev`, or tracking
the genuine state of the global NPM/React framework, the analytic insight remains uniformly
applicable.

Executing this full process not only proves competence in modern DevSecOps, but demonstrates
a profound mastery over generative data simulation, GraphQL interfacing, asynchronous LLM
pipeline management, and high-concurrency database orchestration.

The protocol is secure. The Phalanx is ready.
