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
	cd backend && alembic current
	cd frontend && npm install
	.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
