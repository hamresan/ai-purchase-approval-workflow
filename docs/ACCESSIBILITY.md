# Accessibility review

Stage 9 review target: the implemented React purchase-request workflow.

## Verified in the implementation and automated tests

- Form fields and approval inputs have accessible labels.
- Primary actions use native buttons and remain keyboard operable.
- Loading and submission progress use status semantics where applicable.
- Validation errors use user-facing text rather than raw backend/model output.
- Request tables and item details expose semantic labels/roles.
- Status is communicated with text, not color alone.
- Responsive layouts preserve the same workflow actions on smaller screens.

## Manual release check

Before tagging a release, verify with keyboard-only navigation:

1. Create a purchase request.
2. Open the created request from the dashboard.
3. Open and close each approval dialog.
4. Complete approve, reject, and edit flows.
5. Confirm visible focus, readable errors, and no keyboard trap at desktop and mobile widths.

This project does not claim formal WCAG certification. The checklist records the accessibility baseline reviewed for this release.
