.PHONY: help install dev-install db-up db-migrate run worker beat flower lint test clean

help:
	@echo "canvas-wechat development targets:"
	@echo ""
	@echo "  make install      Install dependencies (pip)"
	@echo "  make dev-install  Install with dev dependencies"
	@echo "  make db-up        Start PostgreSQL + Redis via Docker"
	@echo "  make db-migrate   Run Alembic migrations"
	@echo "  make run          Start FastAPI dev server"
	@echo "  make worker       Start Celery worker"
	@echo "  make beat         Start Celery Beat scheduler"
	@echo "  make flower       Start Celery Flower monitor"
	@echo "  make lint         Run ruff linter"
	@echo "  make test         Run pytest"
	@echo "  make clean        Remove build artifacts"
	@echo "  make docker-up    Start full stack via Docker Compose"

install:
	pip install -e .

dev-install:
	pip install -e '.[dev]'

db-up:
	docker compose up -d postgres redis

db-migrate:
	alembic upgrade head

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	celery -A app.sync.celery_app worker --loglevel=info --concurrency=2

beat:
	celery -A app.sync.celery_app beat --loglevel=info

flower:
	celery -A app.sync.celery_app flower --port=5555

lint:
	ruff check app/ tests/

test:
	pytest -v tests/

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true

docker-up:
	docker compose up -d

docker-down:
	docker compose down
