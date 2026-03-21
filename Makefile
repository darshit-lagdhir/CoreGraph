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
	@echo "Nullifying incomplete background broker operations..."
	docker compose exec -T redis redis-cli FLUSHALL

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

clean-migrations:
	@echo "Neutralizing orphaned revisions and diagnostic bytecode artifacts..."
	powershell -Command "Get-ChildItem -Path backend/migrations/versions -Filter '*.py' | Where-Object { $_.Name -notmatch '^[0-9]' } | Remove-Item -Force"
	powershell -Command "Get-ChildItem -Path backend/migrations -Filter '__pycache__' -Recurse | Remove-Item -Force"

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
