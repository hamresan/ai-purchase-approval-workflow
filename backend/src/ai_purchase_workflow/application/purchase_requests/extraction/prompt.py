from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    EXTRACTED_REQUEST_SCHEMA_VERSION,
    ModelRequest,
)


class PurchaseRequestPromptBuilder:
    def build(self, free_text: str) -> ModelRequest:
        normalized = free_text.strip()
        if not normalized:
            raise ValueError("Purchase request text must not be empty.")

        system_prompt = (
            "Extract purchase-request facts only. Do not invent price, vendor, budget, "
            "availability, approval, or submission facts. Return structured data using "
            f"schema version {EXTRACTED_REQUEST_SCHEMA_VERSION}. "
            "If item identity or quantity is ambiguous, request human review."
        )
        return ModelRequest(system_prompt=system_prompt, user_prompt=normalized)
