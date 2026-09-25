from ai_purchase_workflow.infrastructure.workflows.state import (
    PurchaseRequestWorkflowResult,
    PurchaseRequestWorkflowState,
)


class PurchaseRequestWorkflowResultMapper:
    def map(self, state: PurchaseRequestWorkflowState) -> PurchaseRequestWorkflowResult:
        return PurchaseRequestWorkflowResult(
            checkpoint_id=state["workflow_id"],
            purchase_request_id=state.get("purchase_request_id"),
            status=state["status"],
            needs_human_review=state["status"] == "human_review",
            review_reason=state.get("review_reason"),
            tool_results=state["tool_results"],
        )
