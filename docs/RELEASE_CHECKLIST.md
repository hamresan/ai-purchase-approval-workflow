# Release checklist

## Quality

- [ ] `make check` passes from the repository root.
- [ ] Dockerized Playwright E2E passes for create, approve, reject, and edit.
- [ ] Backend total branch coverage is at least 85%; domain/application coverage remains at least 90%.
- [ ] Frontend total branch coverage is at least 85%; workflow-critical request/approval coverage remains at least 90%.
- [ ] GitHub Actions `quality` workflow is green on the release commit.

## Clean-clone smoke test

- [ ] Clone into a new directory.
- [ ] Copy `.env.example` to `.env`.
- [ ] Run `docker compose up -d postgres`.
- [ ] Run `docker compose build backend frontend`.
- [ ] Run `docker compose run --rm backend uv run alembic upgrade head`.
- [ ] Run `docker compose up -d backend frontend`.
- [ ] Confirm `http://localhost:8000/health` and `http://localhost:5173`.
- [ ] With the Fake provider, create a request and complete approve/reject/edit browser journeys.

## Contract and documentation

- [ ] README commands work from a clean clone.
- [ ] README, OpenAPI, UI labels, and tests describe the same public behavior.
- [ ] `.env.example` contains no secrets.
- [ ] Provider configuration is documented for Fake, Ollama, OpenAI, and OpenRouter.
- [ ] Limitations explicitly mention missing authentication/authorization and fixture-backed commerce data.
- [ ] Screenshots/GIFs, if published, are captured from the verified release UI and contain no private data.

## Repository hygiene

- [ ] MIT license and package metadata are correct.
- [ ] Security and accessibility notes are current.
- [ ] No generated coverage, Playwright, environment, secret, or local database artifacts are committed.
- [ ] No placeholder or development-status wording describes completed functionality as future work.
- [ ] Stage branch is merged only after explicit approval.
