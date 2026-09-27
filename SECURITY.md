# Security

## Supported version

The current `main` branch is the supported development/release line.

## Reporting a vulnerability

Please report security issues privately through GitHub Security Advisories for this repository. Do not open a public issue containing credentials, exploit details, private purchase data, or provider secrets.

Include the affected component, reproduction steps, expected impact, and any suggested mitigation.

## Security boundaries

- Model output and model-generated arguments are untrusted and validated before business-state changes.
- Vendor, catalog, budget, and order-submission facts come from trusted application adapters, not model memory.
- Order submission requires a persisted human approval decision.
- Provider credentials are environment variables and must never be committed, returned by the API, or exposed to the frontend.
- The deterministic Fake model is for development/tests only and is rejected when `APP_ENV=production`.
- Authentication, authorization, and multi-tenancy are not implemented in this v1 demonstration. Do not expose it as a public production procurement service without adding those controls.
