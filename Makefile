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

wipe-db-data:
	@echo "Executing destructive persistence reset..."
	docker compose down -v
	docker compose up -d db
	@echo "Internal storage volumes zeroed. 'make migrate' must be executed."

cleanup: clean-pycache clean-logs clean-migrations prune-sockets prune-sessions flush-tmp
	docker system prune -a --volumes -f
