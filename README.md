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

The browser UI supports request creation, dashboard review, request details, audit timeline, and Approve / Reject / Edit decisions.

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
  ├── trusted fixture adapters
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

The default `.env.example` uses `WORKFLOW_MODEL_PROVIDER=fake`. This deterministic provider requires no external network or API key and is intended for development, demonstration, and CI. It produces the fixture-backed Laptop stand workflow so the complete approval journey can be exercised reliably.

To stop and remove the local stack:

```bash
docker compose down
```

## Use the web interface

1. Open http://localhost:5173.
2. Select **New Purchase Request**.
3. Enter a request of at least 10 characters and optionally a requester name.
4. Submit it. With the default Fake provider, the deterministic extracted request is a Laptop stand for Dana.
5. Open the request and inspect its trusted vendor, price, budget result, draft order, and timeline.
6. Choose **Approve**, **Reject**, or **Edit**.
7. Approve resumes the persisted workflow and submits through the approval gate; Reject records the reason; Edit revalidates trusted data and returns the request to approval review.

Reviewer identity is entered explicitly in the approval dialog. Authentication/authorization is intentionally not part of this v1 demonstration.

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
curl -X POST http://localhost:8000/api/purchase-requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_text": "Dana needs one laptop stand",
    "requester_name": "Dana"
  }'
```

The response is a purchase-request representation with a UUID `id`, requester, items, status, and timestamps. A successful workflow normally reaches `pending_approval`.

List requests:

```bash
curl "http://localhost:8000/api/purchase-requests?status=pending_approval&limit=20&offset=0&order=desc"
```

Read details and audit history:

```bash
curl http://localhost:8000/api/purchase-requests/<request-uuid>
```

Approve:

```bash
curl -X POST http://localhost:8000/api/purchase-requests/<request-uuid>/approval \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "decided_by": "Reviewer Name",
    "reason": "Within budget"
  }'
```

Reject uses `"action": "reject"` and requires a non-empty `reason`. Edit uses `"action": "edit"`, explicit `decided_by`, and an `items` array containing `description` and positive `quantity`; trusted vendor and price are resolved again by the backend.

## Supported behavior

- Free-text purchase-request extraction through a provider-neutral model contract.
- Trusted fixture-backed catalog, vendor, budget, and order adapters.
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

- No authentication, authorization, roles, or multi-tenancy.
- Reviewer identity is manually entered and is not cryptographically verified.
- Catalog, vendor, budget, and order integrations are deterministic fixture adapters rather than ERP/procurement systems.
- No payment or money movement.
- No email/notification system.
- No autonomous purchasing; human approval remains mandatory.
- No generic chat interface.
- External model-provider behavior depends on the selected provider/model and is not required by CI.
- A production deployment would require Auth/AuthZ, real trusted commerce integrations, operational secret management, deployment hardening, and recovery design appropriate to its environment.

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

Stages 0–8 of the implementation roadmap are complete. Stage 9 is release hardening: documentation, clean-clone verification, repository/security/accessibility review, and final quality validation.

Verified UI screenshots/GIFs should be captured from the final release build only and must not contain private request data. They are intentionally not represented by mock images.

## License

MIT — see [LICENSE](LICENSE).
