.PHONY: test lint run-backend run-frontend format security

test:
    pytest tests/

lint:
    ruff check .
    mypy src/

format:
    black src/ tests/

security:
    bandit -r src/

run-backend:
    uvicorn src.fzq_ai.api.app:app --host 0.0.0.0 --port 8000

run-frontend:
    cd frontend-react && npm run dev
