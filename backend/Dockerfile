FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY alembic.ini ./
COPY migrations ./migrations
COPY src ./src

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "ai_purchase_workflow.presentation.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
