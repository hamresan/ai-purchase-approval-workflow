# AI Purchase Approval Workflow

A human-approved purchase-request workflow built with FastAPI, LangChain/LangGraph, PostgreSQL, and a simple React user interface.

> **Status:** Under active development. This README defines the public interface for the first release. Installation commands, API endpoints, and UI screens below will work once the corresponding implementation stages are complete.

## The problem

Purchase requests often arrive as unstructured messages such as: “We need 15 monitors for the design team next week.” Someone then has to find the vendor, check the budget, create a draft order, and obtain approval before money is committed.

This project turns that process into a controlled workflow:

```text
Request → structured extraction → budget/vendor checks → draft order
→ human approval pause → approve, reject, or edit → submit order
```

The AI helps understand a request and choose safe read-only tools. It **cannot submit an order by itself**. Submitting an order always requires explicit human approval.

## What it demonstrates

- Stateful, multi-step workflow orchestration with LangChain/LangGraph
- Tool calling with application services as the source of truth
- PostgreSQL-backed checkpoints so a paused workflow can be resumed
- Human-in-the-loop approval, rejection, and editing
- Policy-based budget controls and deterministic validation
- A non-technical React UI, not only Swagger/API endpoints
- Provider-agnostic LLM support for Fake, Ollama, OpenAI, and OpenRouter

## Planned features

### Workflow

- Convert free-text requests into a structured purchase request
- Look up vendor options and available budget using tools
- Create a draft purchase order
- Pause before the irreversible `submit_order` action
- Let an approver approve, reject, or edit the draft
- Resume the same workflow using its persisted thread/checkpoint
- Keep an audit timeline of workflow steps, decisions, and tool results

### User interface

- Dashboard of pending, approved, rejected, and submitted requests
- Guided form for creating a purchase request without technical knowledge
- Request-detail page showing the extracted request, budget check, vendor, and draft order
- Clear Approve, Reject, and Edit actions
- Readable timeline rather than raw agent messages or JSON

### API

- `POST /api/purchase-requests` — create a request and start the workflow
- `GET /api/purchase-requests` — list requests by status
- `GET /api/purchase-requests/{request_id}` — retrieve request, draft, and audit timeline
- `POST /api/purchase-requests/{request_id}/approval` — approve, reject, or edit a paused draft

## Architecture

```text
frontend/                         # React + Vite user interface
backend/
├── src/ai_purchase_workflow/
│   ├── domain/                   # requests, drafts, policies, workflow states
│   ├── application/              # use cases and explicit ports/contracts
│   ├── infrastructure/           # PostgreSQL, LangChain/LangGraph, Ollama adapters
│   ├── presentation/             # FastAPI routes and HTTP mapping
│   └── composition_root/         # settings and dependency wiring
└── tests/                        # mirrored backend tests
```

The backend follows Clean Architecture: FastAPI, LangChain/LangGraph, database, and model-provider types stay outside the domain and application layers. The frontend communicates only through the documented API.

## Requirements

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js 22+ and npm
- Docker and Docker Compose
- PostgreSQL (provided by Docker Compose for local development)
- An LLM provider is optional: Fake is deterministic, Ollama is local/offline, and OpenAI/OpenRouter are external options

## Quick start with Docker

After implementation, the simplest way to run the full application will be:

```bash
git clone https://github.com/hamresan/ai-purchase-approval-workflow.git
cd ai-purchase-approval-workflow
cp .env.example .env
docker compose up --build
```

Open:

- User interface: `http://localhost:5173`
- API documentation: `http://localhost:8000/docs`

Stop the application:

```bash
docker compose down
```

## Local development

### Backend

```bash
cd backend
uv sync --all-groups
cp .env.example .env
uv run uvicorn ai_purchase_workflow.presentation.app:create_app --factory --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configure the model provider

The workflow depends only on the provider-agnostic model contract. Select the concrete provider at the composition boundary:

```dotenv
WORKFLOW_MODEL_PROVIDER=fake
WORKFLOW_MODEL_NAME=qwen3:8b
WORKFLOW_MODEL_TIMEOUT_SECONDS=30
```

The deterministic `fake` provider is the default for tests and CI and requires no network access.

For local/offline Ollama:

```dotenv
WORKFLOW_MODEL_PROVIDER=ollama
WORKFLOW_MODEL_NAME=qwen3:8b
WORKFLOW_MODEL_BASE_URL=http://localhost:11434/v1
```

For OpenAI:

```dotenv
WORKFLOW_MODEL_PROVIDER=openai
WORKFLOW_MODEL_NAME=<model-name>
OPENAI_API_KEY=<secret>
```

For OpenRouter:

```dotenv
WORKFLOW_MODEL_PROVIDER=openrouter
WORKFLOW_MODEL_NAME=<provider/model>
OPENROUTER_API_KEY=<secret>
```

Ollama, OpenAI, and OpenRouter are accessed through the shared OpenAI-compatible adapter. Provider credentials and transport details remain outside application and workflow code. Model output is always treated as untrusted and passes through the existing structured mapper and validator before business state changes.

## Use the web interface

1. Open the dashboard in a browser.
2. Select **New Purchase Request**.
3. Enter a plain-language request, for example: `15 monitors for the design team, maximum budget $4,500`.
4. Review the extracted details, budget result, vendor choice, and draft order.
5. Select **Approve**, **Reject**, or **Edit**.
6. On approval, the workflow resumes from its saved checkpoint and submits the order.


## API example

Create a purchase request:

```bash
curl -X POST http://localhost:8000/api/purchase-requests \
  -H "Content-Type: application/json" \
  -d '{
    "requester_name": "Ava Chen",
    "request_text": "Please buy 15 monitors for the design team. Keep the total under 4500 USD."
  }'
```

Example response:

```json
{
  "request_id": "pr_01HXYZ",
  "workflow_thread_id": "workflow_pr_01HXYZ",
  "status": "pending_approval",
  "draft_order": {
    "vendor_name": "Example Office Supply",
    "total_amount": "4200.00",
    "currency": "USD"
  },
  "next_action": "human_approval_required"
}
```

Approve a paused request:

```bash
curl -X POST http://localhost:8000/api/purchase-requests/pr_01HXYZ/approval \
  -H "Content-Type: application/json" \
  -d '{ "decision": "approve", "comment": "Within budget." }'
```

## Safety and reliability rules

- Vendor, catalog, budget, and submission data come from tools/services, never from model memory.
- The workflow may use read-only tools and create a draft; `submit_order` is always an approval-gated action.
- Every approval decision is tied to a persisted request and workflow thread.
- An LLM failure, timeout, or malformed tool request must not submit, duplicate, or corrupt an order.
- User-facing UI never exposes raw model prompts, secrets, database errors, or provider credentials.

## Testing and quality

Backend tests mirror production modules and use real FastAPI routes, real PostgreSQL/SQLite test persistence where appropriate, and deterministic model/tool fakes. Frontend tests cover the request form, approval actions, status rendering, and API error states.

```bash
# backend
cd backend
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright src tests
uv run pytest

# frontend
cd frontend
npm run lint
npm run test
```

## Roadmap

- [ ] Backend foundation, database, and health endpoint
- [ ] Request/draft domain model and deterministic workflow policies
- [ ] LangChain/LangGraph tools, state, checkpointing, and pause/resume
- [ ] Human approval API and audit timeline
- [ ] React/Vite dashboard and approval interface
- [x] Provider-agnostic Fake/Ollama/OpenAI/OpenRouter adapter infrastructure and cross-stack resilience
- [ ] Release hardening and public repository polish

## License

This project will be released under the MIT License.