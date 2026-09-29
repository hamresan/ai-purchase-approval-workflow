# AI Purchase Approval Workflow

[![quality](https://github.com/hamresan/ai-purchase-approval-workflow/actions/workflows/quality.yml/badge.svg)](https://github.com/hamresan/ai-purchase-approval-workflow/actions/workflows/quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A human-approved purchase-request workflow built with FastAPI, LangGraph, PostgreSQL, and React.

The project demonstrates how an LLM can interpret a free-text request without becoming the source of truth for purchasing decisions. Trusted application services resolve catalog, vendor, budget, and order data, while an irreversible submission always requires an explicit human approval.

## Workflow

```text
Free-text request
    ↓
Structured extraction (untrusted model output)
    ↓
Validation + trusted catalog/vendor/budget checks
    ↓
Persisted draft order
    ↓
LangGraph checkpoint + human approval pause
    ├── Reject → rejected
    ├── Edit → trusted revalidation → pending approval
    └── Approve → resume checkpoint → approval-gated submission
```

The purchase APIs and browser workflow are protected by passwordless Identity authentication and application-owned roles. The browser refreshes expired access tokens through Identity session refresh and signs the user out when the refresh session is no longer valid.

## Architecture

```text
Browser (React/Vite)
        │ HTTP
        ▼
Presentation (FastAPI)
        │
        ▼
Application ──────► Domain policies/entities
        │ contracts
        ▼
Infrastructure
  ├── PostgreSQL repositories
  ├── LangGraph workflow/checkpoints
  ├── PostgreSQL trusted catalog/budget readers
  └── model adapters
        ├── Fake
        ├── Ollama
        ├── OpenAI
        └── OpenRouter
```

Dependency direction stays inward: domain/application code does not depend on FastAPI, SQLAlchemy, LangGraph, or provider SDK types. Provider selection happens in the composition root. PostgreSQL business records are authoritative; LangGraph checkpoints preserve execution state.

## Requirements

For Docker usage:

- Docker with Docker Compose

For local development:

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 22+
- npm

## Quick start — clean clone with deterministic Fake provider

```bash
git clone https://github.com/hamresan/ai-purchase-approval-workflow.git
cd ai-purchase-approval-workflow
cp .env.example .env

docker compose up -d postgres
docker compose build backend frontend
docker compose run --rm backend uv run alembic upgrade head
docker compose up -d backend frontend
```

Open:

- UI: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

The default `.env.example` uses `WORKFLOW_MODEL_PROVIDER=fake`. This deterministic provider requires no external network or API key and is intended for development, demonstration, and CI. It produces a deterministic Laptop stand extraction so the complete approval journey can be exercised reliably against persisted trusted catalog and budget data.

To stop and remove the local stack:

```bash
docker compose down
```

## Authentication and authorization

Passwordless registration, login, session refresh, and revocation are provided by `hamresan-identity` under `/identity`. OTP notification intent flows through `hamresan-notification`; durable provider delivery is added in the notification stage.

Successful first-time registration provisions the application `REQUESTER` role. Application authorization owns `REQUESTER`, `APPROVER`, and `ADMIN` roles. Requester and approver identity are derived from the authenticated principal rather than request payloads or model output, and self-approval is rejected.

The first administrator is bootstrapped explicitly after that person has registered:

```bash
cd backend
uv run python -m ai_purchase_workflow.operations.bootstrap_admin --mobile +96891234567
```

The command resolves an already registered mobile identity through the public Identity contract, is idempotent, and grants `ADMIN` to that user; normal registration never grants `ADMIN`.

All `/api/purchase-requests` calls require a Bearer access token. The browser provides mobile OTP login/registration, post-verification profile setup for new users, session refresh, and sign-out/revocation.

## Model providers

Common settings:

```dotenv
WORKFLOW_MODEL_PROVIDER=fake
WORKFLOW_MODEL_NAME=qwen3:8b
WORKFLOW_MODEL_TIMEOUT_SECONDS=30
WORKFLOW_MODEL_BASE_URL=
```

### Fake

```dotenv
APP_ENV=development
WORKFLOW_MODEL_PROVIDER=fake
```

Fake is deterministic and used by tests/CI. The application rejects Fake when `APP_ENV=production`.

### Ollama — local/offline

Run an OpenAI-compatible Ollama endpoint and configure:

```dotenv
WORKFLOW_MODEL_PROVIDER=ollama
WORKFLOW_MODEL_NAME=qwen3:8b
WORKFLOW_MODEL_BASE_URL=http://localhost:11434/v1
```

If the backend itself runs inside Docker, `localhost` refers to the backend container. Configure a base URL reachable from that container or run the backend locally.

### OpenAI

```dotenv
WORKFLOW_MODEL_PROVIDER=openai
WORKFLOW_MODEL_NAME=<supported-model>
OPENAI_API_KEY=<secret>
```

### OpenRouter

```dotenv
WORKFLOW_MODEL_PROVIDER=openrouter
WORKFLOW_MODEL_NAME=<provider/model>
OPENROUTER_API_KEY=<secret>
```

Ollama, OpenAI, and OpenRouter use the focused OpenAI-compatible infrastructure adapter. Credentials remain outside application/workflow code. Provider output is untrusted until it passes the structured mapper and validator.

## API

The interactive OpenAPI document at `/docs` is the canonical field-level reference.

Create and start a free-text workflow:

```bash
curl -X POST http://localhost:8000/api/purchase-requests \\
  -H "Authorization: Bearer <access-token>" \\
  -H "Content-Type: application/json" \\
  -d '{"request_text": "I need one laptop stand"}'
```

The response is a purchase-request representation with a UUID `id`, requester, items, status, and timestamps. A successful workflow normally reaches `pending_approval`.

List requests:

```bash
curl -H "Authorization: Bearer <access-token>" \\
  "http://localhost:8000/api/purchase-requests?status=pending_approval&limit=20&offset=0&order=desc"
```

Read details and audit history:

```bash
curl -H "Authorization: Bearer <access-token>" \\
  http://localhost:8000/api/purchase-requests/<request-uuid>
```

Approve:

```bash
curl -X POST http://localhost:8000/api/purchase-requests/<request-uuid>/approval \\
  -H "Authorization: Bearer <access-token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "approve",
    "reason": "Within budget"
  }'
```

Reject uses `"action": "reject"` and requires a non-empty `reason`. Edit uses `"action": "edit"` and an `items` array containing `description` and positive `quantity`; the authenticated principal is the authoritative decision actor, and trusted vendor and price are resolved again by the backend.

## Supported behavior

- Free-text purchase-request extraction through a provider-neutral model contract.
- PostgreSQL-backed trusted catalog, vendor, availability, user/department budget data, plus the focused fixture order-submission boundary.
- PostgreSQL business persistence and LangGraph PostgreSQL checkpoints.
- Human Approve / Reject / Edit flows.
- Approval-gated order submission.
- Audit timeline and safe user-facing errors.
- Idempotent structured request creation support.
- Fake, Ollama, OpenAI, and OpenRouter model configuration.
- Responsive React dashboard, creation form, request detail, and approval dialogs.

## Safety and reliability

- Model output is never a trusted source for vendor, price, budget, or submission state.
- Trusted business state lives in PostgreSQL; workflow checkpoints are execution state.
- `submit_order` requires an approved persisted decision.
- Duplicate/concurrent approval protection prevents multiple workflow resumes for the same decision path.
- Provider timeout, unavailable-provider, and malformed-output paths fail safely.
- API responses and UI do not expose raw prompts, credentials, database errors, or provider internals.
- Secrets belong in environment variables; `.env` is ignored by Git.

See [SECURITY.md](SECURITY.md) for the security boundary and reporting guidance.

## Limitations

This repository is a focused workflow demonstration, not a production procurement platform.

- No multi-tenancy.
- Catalog, vendor, availability, and budget data are application-owned PostgreSQL records; order submission remains a deterministic fixture boundary rather than an ERP/procurement integration.
- No payment or money movement.
- OTP notification intent is integrated through `hamresan-notification`, but durable SMS/email delivery and workflow notifications are not implemented yet.
- No autonomous purchasing; human approval remains mandatory.
- No generic chat interface.
- External model-provider behavior depends on the selected provider/model and is not required by CI.
- A production deployment would require real trusted commerce integrations, durable notification delivery, distributed rate limiting, operational secret management, deployment hardening, and recovery design appropriate to its environment.

## Development

Backend:

```bash
cd backend
uv sync --all-groups
uv run uvicorn ai_purchase_workflow.presentation.app:create_app --factory --reload
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

For local backend execution, set `DATABASE_URL` to a PostgreSQL address reachable from the host rather than the Docker service hostname.

## Tests and quality gates

Run all non-E2E quality gates:

```bash
make check
```

This runs Ruff, Ruff format check, strict Pyright, backend pytest with branch coverage, ESLint, TypeScript typecheck, and Vitest coverage.

Playwright E2E exercises the real Dockerized frontend/backend/PostgreSQL/workflow stack with deterministic model behavior. GitHub Actions runs the quality gates, migrations, Docker stack, and browser journeys on stage branches, pull requests, and `main`.

Coverage floors:

- backend total branch coverage: 85%+
- domain/application: 90%+
- frontend total branch coverage: 85%+
- workflow-critical request/approval frontend: 90%+

Release verification is documented in [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md). Accessibility review notes are in [docs/ACCESSIBILITY.md](docs/ACCESSIBILITY.md).

## Repository structure

```text
backend/
├── src/ai_purchase_workflow/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── presentation/
│   └── composition_root/
└── tests/

frontend/
├── src/
│   ├── api/
│   ├── app/
│   ├── components/
│   └── features/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/

docs/
├── ACCESSIBILITY.md
└── RELEASE_CHECKLIST.md
```

## Release status

Stages 0–10 are complete. Stage 11 adds application-owned organization membership plus PostgreSQL-backed trusted catalog, vendor, availability, and user/department budget persistence.

Verified UI screenshots/GIFs should be captured from the final release build only and must not contain private request data. They are intentionally not represented by mock images.

## License

MIT — see [LICENSE](LICENSE).
