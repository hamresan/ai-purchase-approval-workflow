from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.preparation import (
    PrepareExtractedPurchaseRequest,
)
from ai_purchase_workflow.infrastructure.workflows.state import (
    PurchaseRequestWorkflowState,
)


class ExtractPurchaseRequestNode:
    def __init__(self, extractor: ExtractPurchaseRequest) -> None:
        self._extractor = extractor

    async def __call__(
        self,
        state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState:
        outcome = await self._extractor.execute(state["free_text"])
        updated = state.copy()
        if outcome.needs_human_review or outcome.extracted_request is None:
            updated["status"] = "human_review"
            updated["review_reason"] = (
                outcome.review_reason or "Extraction requires human review."
            )
            return updated

        updated["extracted_request"] = outcome.extracted_request
        updated["status"] = "extracted"
        return updated


class PreparePurchaseRequestNode:
    def __init__(self, preparer: PrepareExtractedPurchaseRequest) -> None:
        self._preparer = preparer

    async def __call__(
        self,
        state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState:
        extracted = state.get("extracted_request")
        if extracted is None:
            updated = state.copy()
            updated["status"] = "human_review"
            updated["review_reason"] = "Extracted request is missing."
            return updated

        try:
            request = await self._preparer.execute(extracted)
        except Exception as error:
            updated = state.copy()
            updated["status"] = "human_review"
            updated["review_reason"] = f"Trusted tool execution failed: {error}"
            updated["tool_results"] = ("prepare_failed",)
            return updated

        updated = state.copy()
        updated["purchase_request_id"] = request.id
        updated["status"] = "pending_approval"
        updated["tool_results"] = (
            "trusted_data_resolved",
            "draft_order_created",
            "budget_checked",
        )
        return updated
