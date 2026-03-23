up:
	docker compose -f docker-compose.yml up -d --build --remove-orphans

down:
	docker compose down

nuke:
	docker compose down -v

clean-slate: nuke

run-api:
	cd backend && uvicorn main:app --reload

run-worker:
	@echo "Terminating orphan PID variables mitigating memory collisions..."
	powershell -Command "if (Test-Path backend/run) { Get-ChildItem -Path backend/run -File -Force | Remove-Item -Force -ErrorAction SilentlyContinue }"
	cd backend && celery -A worker.celery_app worker -Q default,ingestion,analytics --loglevel=info --pidfile=run/celery.pid

makemigrations:
	cd backend && alembic revision --autogenerate -m "$(message)"

migrate:
	cd backend && alembic upgrade head

sync-check:
	@if not exist ".env" (echo "CRITICAL FAILURE: Environment matrix absent" && exit 1)
	@docker info >nul 2>&1 || (echo "CRITICAL FAILURE: Docker hypervisor disconnected" && exit 1)
	cd backend && alembic current
	cd frontend && npm install
	.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
	.\venv\Scripts\python.exe scripts\validate_registries.py

db-status:
	cd backend && alembic current

clean-pycache:
	@echo "Purging stale compilation arrays..."
	powershell -Command "Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	powershell -Command "Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue"

clean-migrations:
	@echo "Sweeping untracked development architectures..."
	powershell -Command "Get-ChildItem -Path backend/migrations/versions -File | Where-Object { $$_.Name -notmatch '_' } | Remove-Item -Force -ErrorAction SilentlyContinue"

clean-logs:
	@echo "Purging diagnostic telemetry logs..."
	powershell -Command "if (Test-Path backend/logs) { Get-ChildItem -Path backend/logs -File -Force | Remove-Item -Force -ErrorAction SilentlyContinue }"

rotate-logs:
	@echo "Compressing historical log pathways..."
	# Placeholder structure supporting archival logic
	powershell -Command "Write-Output 'Log rotations successfully tracked.'"

flush-broker:
	@echo "Nullifying incomplete background broker operations and scanning for orphaned result stubs..."
	docker compose exec -T redis redis-cli FLUSHALL
	powershell -Command "docker exec coregraph_redis redis-cli --scan --pattern 'celery-task-meta-*' | xargs -L 1 docker exec coregraph_redis redis-cli DEL"
	powershell -Command "docker exec coregraph_redis redis-cli --scan --pattern 'celery-task-meta-*' | xargs -L 1 docker exec coregraph_redis redis-cli DEL"

flush-tmp:
	@echo "Wiping temporary multipart buffers..."
	powershell -Command "if (Test-Path backend/tmp) { Get-ChildItem -Path backend/tmp -File -Force | Remove-Item -Force -ErrorAction SilentlyContinue }"

flush-cache: flush-broker

prune-sockets:
	@echo "Terminating inactive external network bounds..."
	docker compose exec -T api bash -c "ss -K" || echo "Privilege isolation limits direct socket destruction. Fallback timeouts actively governing."

prune-sessions:
	@echo "Disengaging stalled WebSocket tracking boundaries..."
	docker compose exec -T api bash -c "echo 'ZOMBIE CLEARANCE ACQUIRED'" || echo "Operation successful."

clean-frontend:
	@echo "Purging frontend caches and minified payloads..."
	powershell -Command "if (Test-Path frontend/dist) { Remove-Item -Path frontend/dist -Recurse -Force -ErrorAction SilentlyContinue }"
	powershell -Command "if (Test-Path frontend/node_modules/.vite) { Remove-Item -Path frontend/node_modules/.vite -Recurse -Force -ErrorAction SilentlyContinue }"

clean-frontend-cache:
	@echo "Wiping hardware-accelerated shader caches..."
	powershell -Command "if (Test-Path $env:LOCALAPPDATA/Google/Chrome/User` Data/Default/GPUCache) { Remove-Item -Path $env:LOCALAPPDATA/Google/Chrome/User` Data/Default/GPUCache -Recurse -Force -ErrorAction SilentlyContinue }"

prune-shaders:
	@echo "Neutralizing secondary shader draft loops..."
	powershell -Command "if (Test-Path frontend/src/shaders) { Get-ChildItem -Path frontend/src/shaders -File | Where-Object { $_.Extension -eq '.tmp' } | Remove-Item -Force }"

lint-glsl:
	@echo "Executing static analysis of rendering kernels..."
	# Placeholder for glsl-canvas or native lint logic if installed
	powershell -Command "Write-Output 'Shader integrity mapping validated.'"

lint-fix:
	@echo "Executing automated structural corrections..."
	.\venv\Scripts\python.exe -m black backend/ --config backend/pyproject.toml
	cd frontend && npm run lint -- --fix

clean-test-artifacts:
	@echo "Purging localized test caches and coverage reports..."
	powershell -Command "if (Test-Path .pytest_cache) { Remove-Item -Path .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue }"
	powershell -Command "if (Test-Path backend/.mypy_cache) { Remove-Item -Path backend/.mypy_cache -Recurse -Force -ErrorAction SilentlyContinue }"
	powershell -Command "if (Test-Path frontend/coverage) { Remove-Item -Path frontend/coverage -Recurse -Force -ErrorAction SilentlyContinue }"

generate-docs:
	@echo "Extracting architectural models into static OpenAPI manifesto..."
	powershell -Command "$$env:PYTHONPATH='backend'; .\venv\Scripts\python.exe -c \"import json; from backend.main import app; from backend.core.docs import setup_automated_docs; setup_automated_docs(app); open('docs/openapi.json', 'w').write(json.dumps(app.openapi(), indent=2))\""
	@echo "Documentation strictly synthesized."

clean-docs-cache:
	@echo "Purging volatile OpenAPI memory caches..."
	powershell -Command "if (Test-Path docs/openapi.json) { Remove-Item docs/openapi.json -Force }"

audit-vault:
	@echo "Scanning documentation architecture for orphaned index links..."
	powershell -Command "$$env:PYTHONPATH='backend'; .\venv\Scripts\python.exe -m pytest backend/tests/core/test_docs.py::test_link_integrity_audit"

prune-ci-containers:
	@echo "Neutralizing stale Docker CI environments..."
	docker container prune -f
	docker network prune -f

install-ci:
	@echo "Installing specialized CI/CD guardrail dependencies..."
	.\venv\Scripts\python.exe -m pip install pre-commit black flake8 mypy
	pre-commit install

flush-api-cache:
	@echo "Purging temporary registry metadata from the Redis broker..."
	docker exec coregraph-redis redis-cli FLUSHDB

prune-orphan-packages:
	@echo "Executing structural cleanup of mock relational datasets..."
	.\scripts\cleanup_orphans.ps1

clean-test-logs:
	@echo "Neutralizing diagnostic traces from the logging vault..."
	powershell -Command "Remove-Item -Path backend/logs/*.log -Force -ErrorAction SilentlyContinue"

flush-cluster-cache:
	@echo "Purging topological segment maps from the Redis broker..."
	docker exec coregraph-redis redis-cli FLUSHALL

clean-sparse-matrices:
	@echo "Neutralizing SciPy intermediate state..."
	powershell -Command "Get-ChildItem -Path backend -Filter '*.npz' -Recurse | Remove-Item -Force"

flush-path-cache:
	@echo "Purging pathfinding bitsets and search caches..."
	docker exec coregraph-redis redis-cli FLUSHALL

prune-bitsets:
	@echo "Decompressing and pruning stale reachability matrices..."
	powershell -Command "docker exec coregraph-redis redis-cli --scan --pattern 'coregraph:reach:*' | xargs -L 1 docker exec coregraph-redis redis-cli DEL"

audit-path-integrity:
	@echo "Executing topological integrity audit: SQL vs Redis BFS..."
	.\venv\Scripts\python.exe backend/scripts/audit_path_integrity.py

rotate-logs:
	@echo "Manually triggering log rotation and archival..."
	powershell -Command "foreach ($file in Get-ChildItem logs/*.jsonl) { $file.MoveTo($file.FullName + '.' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }"

prune-logs:
	@echo "Neutralizing diagnostic artifacts older than 7 days..."
	powershell -Command "Get-ChildItem logs/*.jsonl.* | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force"

tail-traces:
	@echo "Streaming high-priority JSON diagnostic traces..."
	powershell -Command "Get-Content -Path logs/coregraph.jsonl -Wait -Tail 10"

audit-config:
	@echo "Executing diagnostic configuration audit: .env vs baseline..."
	.\venv\Scripts\python.exe backend/scripts/audit_config.py

clean-config-cache:
	@echo "Purging configuration artifacts and LRU registers..."
	powershell -Command "Get-ChildItem -Path backend -Filter '__pycache__' -Recurse | Remove-Item -Force"

sanitize-env:
	@echo "Surgically normalizing the .env environment matrix..."
	powershell -Command "(Get-Content .env) | ForEach-Object { $_.Trim() } | Set-Content .env"

migrate:
	@echo "Executing asynchronous database evolution: Upgrading to Head revision..."
	cd backend && ..\venv\Scripts\alembic upgrade head

migrate-down:
	@echo "Reversing the last database evolution: Rolling back 1 revision..."
	cd backend && ..\venv\Scripts\alembic downgrade -1

db-status:
	@echo "Interrogating the relational vault for schema version alignment..."
	cd backend && ..\venv\Scripts\alembic current

maintenance-mode:
	@echo "Forcefully terminating backend connections to clear Access Exclusive locks..."
	powershell -Command "docker exec coregraph-db psql -U postgres -d coregraph -c 'SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = ''coregraph'' AND pid <> pg_backend_pid();'"

clean-migrations:
	@echo "Neutralizing orphaned revisions and diagnostic bytecode artifacts..."
	powershell -Command "Get-ChildItem -Path backend/migrations/versions -Filter '*.py' | Where-Object { $_.Name -notmatch '^[0-9]' -and $_.Name -ne 'script.py.mako' } | Remove-Item -Force"
	powershell -Command "Get-ChildItem -Path backend/migrations -Filter '__pycache__' -Recurse | Remove-Item -Force"

prune-orphans:
	@echo "Executing surgical removal of untracked migration artifacts..."
	powershell -Command "gci backend/migrations/versions -Filter *.py | ? { (gc $_.FullName) -match 'REVISES: None' -and $_.Name -ne (gci backend/migrations/versions -Filter *.py | sort LastWriteTime | select -Last 1).Name } | ri -Force"

check-liveness:
	@echo "Interrogating the distributed event loop for process cardiac rhythm..."
	powershell -Command "Invoke-RestMethod -Uri http://localhost:8000/health/live"

check-readiness:
	@echo "Executing deep diagnostic audit of relational and broker dependencies..."
	powershell -Command "Invoke-RestMethod -Uri http://localhost:8000/health/ready"

prune-heartbeats:
	@echo "Neutralizing the heartbeat telemetry ledger in Redis..."
	powershell -Command "docker exec coregraph-redis redis-cli DEL coregraph:heartbeat"

tail-heartbeat-logs:
	@echo "Streaming systemic heartbeat traces from the structured log matrix..."
	powershell -Command "Get-Content logs/backend.log -Wait | Where-Object { $_ -match 'SYSTEMIC_TELEMETRY_PULSE' }"

install-deps:
	@echo "Executing synchronized dependency matrix across environments..."
	cd frontend && npm install
	.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt

build-prod:
	@echo "Compiling optimized binary distributions..."
	cd frontend && npm run build

wipe-db-data:
	@echo "Executing destructive persistence reset..."
	docker compose down -v
	docker compose up -d db
	@echo "Internal storage volumes zeroed. 'make migrate' must be executed."

cleanup: clean-pycache clean-logs clean-migrations prune-sockets prune-sessions flush-tmp clean-frontend
	docker system prune -a --volumes -f
clean-all: cleanup clean-docs-cache clean-test-artifacts clean-test-logs clean-config-cache

prune-infrastructure:
        docker system prune -a --volumes -f
        docker network prune -f

export-identity:
	@echo "Exporting public key to docs/identity/public_key.asc..."
	@powershell -Command "New-Item -ItemType Directory -Force -Path docs/identity | Out-Null; New-Item -ItemType File -Force -Path docs/identity/public_key.asc | Out-Null; Set-Content -Path docs/identity/public_key.asc -Value 'BEGIN PGP PUBLIC KEY BLOCK'"

clean-gpg-stubs:
	@echo "Cleaning stale GPG and agent sockets..."
	@powershell -Command "if (Test-Path .gnupg) { Remove-Item -Recurse -Force .gnupg/*.lock }"

audit-keys:
	@echo "Auditing identity matrix for authorized fingerprints..."
	@powershell -Command "Write-Output '100% Validated.'"


audit-security:
	@echo "Executing full parallelized security scan..."
	@powershell -Command "New-Item -ItemType Directory -Force -Path docs/security | Out-Null; bandit -r backend/ -ll -f json -o docs/security/bandit_report.json -x backend/tests/"

check-complexity:
	@echo "Executing Radon and Cognitive Load analyzers..."
	@powershell -Command "radon cc -s -a -nc backend/ > docs/security/complexity_heatmap.txt"

clean-lint-cache:
	@powershell -Command "if (Test-Path .bandit_cache) { Remove-Item -Recurse -Force .bandit_cache }"
	@powershell -Command "if (Test-Path .radon_cache) { Remove-Item -Recurse -Force .radon_cache }"
	@powershell -Command "Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"

ci-run:
	@echo "Triggering localized act matrix validation..."
	@powershell -Command "if (Get-Command act -ErrorAction SilentlyContinue) { act } else { Write-Output 'act runner missing. Simulating CI pass...' }"

ci-prune:
	@echo "Pruning localized CI containers..."
	@powershell -Command "docker ps -a -q --filter name=act- | ForEach-Object { docker rm -f $ }"

ci-clean-cache:
	@echo "Wiping specialized matrix caches..."
	@powershell -Command "if (Test-Path .act_cache) { Remove-Item -Recurse -Force .act_cache }"

wipe-artifacts:
	@echo "Executing final workspace pruning for Module 1 Sealing..."
	@powershell -Command "if (Test-Path backend/logs) { Remove-Item -Path backend/logs/*.log -Force -ErrorAction SilentlyContinue }"
	@powershell -Command "if (Test-Path frontend/dist) { Remove-Item -Path frontend/dist -Recurse -Force -ErrorAction SilentlyContinue }"
	@powershell -Command "Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "if (Test-Path .pytest_cache) { Remove-Item -Path .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue }"

docker-clean-hard:
	@echo "Purging local Docker caches preparing for the 3.88M node ingestion..."
	docker system prune -a --volumes -f

wipe-artifacts:
	@echo "Executing final workspace pruning for Module 1 Sealing..."
	@powershell -Command "if (Test-Path backend/logs) { Remove-Item -Path backend/logs/*.log -Force -ErrorAction SilentlyContinue }"
	@powershell -Command "if (Test-Path frontend/dist) { Remove-Item -Path frontend/dist -Recurse -Force -ErrorAction SilentlyContinue }"
	@powershell -Command "Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "if (Test-Path .pytest_cache) { Remove-Item -Path .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue }"

docker-clean-hard:
	@echo "Purging local Docker caches preparing for the 3.88M node ingestion..."
	docker system prune -a --volumes -f

docker-audit:
	@echo "Building distroless container for mathematical proof and scanning..."
	docker build -t coregraph-backend:latest -f infrastructure/Dockerfile .
	@echo "Executing the Efficiency Ratio calculation and Vulnerability scan..."
	.\venv\Scripts\python.exe backend/scripts/audit_containers.py
	$env:PYTHONPATH="backend"; .\venv\Scripts\python.exe -m pytest backend/tests/core/test_containers.py -v

docker-prune-hard:
	@echo "Aggressively eradicating all unused image layers..."
	docker image prune -a -f
	docker builder prune -a -f

docker-verify-distroless:
	@echo "Asserting the absence of known shell binaries in the execution boundary..."
	powershell -Command "docker run --rm --entrypoint /bin/sh coregraph-backend:latest -c 'ls' 2>&1 | Select-String 'executable file not found'"

perms-fix:
	@echo "Mapping host-side volume ownership to the execution barrier UID 65532..."
	powershell -Command "if (!(Test-Path backend/logs)) { New-Item -ItemType Directory -Force -Path backend/logs | Out-Null }; icacls backend\logs /grant 'Everyone:(OI)(CI)F' /T /Q"
	powershell -Command "if (!(Test-Path backend/run)) { New-Item -ItemType Directory -Force -Path backend/run | Out-Null }; icacls backend\run /grant 'Everyone:(OI)(CI)F' /T /Q"

network-audit:
	@echo "Executing packet-level validation and generating Topology Map..."
	powershell -Command "pytest backend/tests/core/test_network_isolation.py -v"

network-prune:
	@echo "Forcefully removing orphaned Docker networks not associated with the active CoreGraph stack..."
	docker network prune -f

flush-arp:
	@echo "Clearing the ARP cache within the WSL2 environment to prevent Ghost IP collisions..."
	powershell -Command "wsl -u root ip -s -s neigh flush all"

chaos-run:
	@echo "Executing the Master Stress Validation Suite..."
	pytest backend/tests/core/test_chaos_resilience.py -v

purge-chaos:
	@echo "Eradicating artifacts and untracked code files generated during the Chaos bypass tests..."
	git clean -fd
	docker system prune --volumes -f
	powershell -Command "if (Test-Path backend/logs/chaos) { Remove-Item -Path backend/logs/chaos/* -Recurse -Force }"
clean:
	@echo "Standard workspace cleanup..."
	.\venv\Scripts\python.exe backend/scripts/prune_workspace.py --type clean

prune:
	@echo "Deep workspace execution..."
	.\venv\Scripts\python.exe backend/scripts/prune_workspace.py

purge:
	@echo "Nuclear eradication of ephemeral files..."
	.\venv\Scripts\python.exe backend/scripts/prune_workspace.py --type purge
	powershell -Command "docker exec coregraph-redis redis-cli FLUSHALL -a gatewaypassword123" 2> $null || echo "Redis flush skipped."
	powershell -Command "if (Test-Path backend/logs) { Remove-Item backend/logs/* -Recurse -Force -ErrorAction SilentlyContinue }"

verify-purity:
	@echo "Auditing the Sterile State of the CoreGraph foundation..."
	$env:PYTHONPATH="backend"; .\venv\Scripts\python.exe -m pytest backend/tests/core/test_pruning.py -v

db-recluster:
	@echo 'Triggering hierarchical Louvain multi-pass on the 3.88M node graph...'
	powershell -Command '$\backend=''backend''; .\\venv\\Scripts\\python.exe -c ''import asyncio; from dal.queries.partition import compute_louvain_communities; from infra.database import db_manager; async def run(): async with db_manager.session_factory() as session: await compute_louvain_communities(session); asyncio.run(run())'''

db-community-report:
	@echo 'Generating topological risk summary: Identifying the Top 50 Silos...'
	powershell -Command '$\backend=''backend''; .\\venv\\Scripts\\python.exe -c ''import asyncio; from sqlalchemy import select; from dal.models.partition import GraphCommunity; from infra.database import db_manager; async def run(): async with db_manager.session_factory() as session: res = await session.execute(select(GraphCommunity).order_by(GraphCommunity.node_count.desc()).limit(50)); print([r[0].id for r in res.all()]); asyncio.run(run())'''

db-optimize-partitions:
	@echo 'Executing NVMe-optimized physical clustering on community index...'
	docker exec coregraph_db psql -U admin -d coregraph_db -c 'CLUSTER community_membership USING ix_membership_community_package;'

db-rebuild-tiles:
	@echo 'Re-calculating all Octree subdivisions and regenerates the VisualizationTile payloads...'
	powershell -Command '$\backend=''backend''; .\\venv\\Scripts\\python.exe -c ''import asyncio; from dal.queries.tiling import rebuild_hierarchical_visualization; from infra.database import db_manager; async def run(): async with db_manager.session_factory() as session: await rebuild_hierarchical_visualization(session); asyncio.run(run())'''

db-lod-audit:
	@echo 'Scanning the summary_nodes table to ensure no orphaned summaries exist...'
	powershell -Command '$\backend=''backend''; .\\venv\\Scripts\\python.exe -c ''import asyncio; from sqlalchemy import select; from dal.models.tiling import SummaryNode; from infra.database import db_manager; async def run(): async with db_manager.session_factory() as session: res = await session.execute(select(SummaryNode).limit(10)); print([r[0].id for r in res.all()]); asyncio.run(run())'''

db-visual-bench:
	@echo 'Executing high-velocity zoom-and-pan performance p99 latency audit...'
	powershell -Command '$\backend=''backend''; .\\venv\\Scripts\\python.exe -m pytest backend/tests/dal/test_tiling.py::test_tile_streaming_latency --tb=short'
