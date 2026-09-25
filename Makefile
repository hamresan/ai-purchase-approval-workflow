.PHONY: check backend-check frontend-check test

check: backend-check frontend-check

backend-check:
	cd backend && uv run ruff check src tests
	cd backend && uv run ruff format --check src tests
	cd backend && uv run pyright src tests
	cd backend && uv run pytest --cov=ai_purchase_workflow --cov-branch --cov-report=term-missing --cov-fail-under=85

frontend-check:
	cd frontend && npm run lint
	cd frontend && npm run typecheck
	cd frontend && npm run test:coverage

test:
	cd backend && uv run pytest
	cd frontend && npm test -- --run
