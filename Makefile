.PHONY: test lint run-backend run-frontend format security install

# Install the src-layout package in editable mode (required before
# `run-backend` / `test` so that `from fzq_ai...` is importable).
install:
	pip install -e .

test:
	pytest tests/

lint:
	ruff check .
	mypy src/

format:
	black src/ tests/

security:
	bandit -r src/

# Requires the package to be installed first: run `make install`
# (or `pip install -e .`) once before `make run-backend`.
run-backend: install
	uvicorn src.fzq_ai.api.app:app --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend-react && npm run dev
