.PHONY: setup backend frontend check
setup:
	uv sync --frozen
	cd frontend && npm ci
	uv run python backend/manage.py migrate
backend:
	uv run python backend/manage.py runserver 127.0.0.1:8000
frontend:
	cd frontend && npm run dev
check:
	uv run ruff check .
	uv run ruff format --check .
	uv run python backend/manage.py check
	uv run python backend/manage.py makemigrations --check --dry-run
	uv run python backend/manage.py test core accounts labels
	cd frontend && npm run build
