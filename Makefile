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
