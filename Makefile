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
	cd backend && celery -A core.celery_app worker --loglevel=info

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

wipe-db-data:
	@echo "Executing destructive persistence reset..."
	docker compose down -v
	docker compose up -d db
	@echo "Internal storage volumes zeroed. 'make migrate' must be executed."

cleanup:
	docker system prune -a --volumes -f
