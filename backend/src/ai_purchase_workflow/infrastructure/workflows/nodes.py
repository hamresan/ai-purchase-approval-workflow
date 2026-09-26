from langgraph.types import interrupt

from ai_purchase_workflow.application.observability import WorkflowObservation, WorkflowObserver
from ai_purchase_workflow.application.purchase_requests.extracted_preparation import (
    PrepareExtractedPurchaseRequest,
    PurchaseRequestPreparationError,
)
from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.preparation import (
    SubmitPurchaseRequest,
)
from ai_purchase_workflow.application.workflows import WorkflowThreadRepository
from ai_purchase_workflow.infrastructure.workflows.state import (
    ApprovalResume,
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
            updated["review_reason"] = outcome.review_reason or "Extraction requires human review."
            return updated

        updated["extracted_request"] = outcome.extracted_request
        updated["status"] = "extracted"
        return updated


class PreparePurchaseRequestNode:
    def __init__(
        self,
        preparer: PrepareExtractedPurchaseRequest,
        workflow_threads: WorkflowThreadRepository,
        observer: WorkflowObserver,
    ) -> None:
        self._preparer = preparer
        self._workflow_threads = workflow_threads
        self._observer = observer

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
        except PurchaseRequestPreparationError as error:
            updated = state.copy()
            updated["status"] = "human_review"
            updated["review_reason"] = f"Trusted tool execution failed: {error}"
            updated["tool_results"] = ("prepare_failed",)
            self._observer.record(
                WorkflowObservation(
                    event="workflow_fallback",
                    workflow_thread_id=state["workflow_id"],
                    state_transition="human_review",
                    tool_name="prepare_purchase_request",
                    fallback_occurred=True,
                )
            )
            return updated

        await self._workflow_threads.bind(request.id, state["workflow_id"])
        updated = state.copy()
        updated["purchase_request_id"] = request.id
        updated["status"] = "pending_approval"
        updated["tool_results"] = (
            "trusted_data_resolved",
            "draft_order_created",
            "budget_checked",
            "approval_paused",
        )
        for tool_name in ("find_vendor", "create_draft_order", "check_budget"):
            self._observer.record(
                WorkflowObservation(
                    event="workflow_tool_completed",
                    workflow_thread_id=state["workflow_id"],
                    purchase_request_id=request.id,
                    state_transition="pending_approval",
                    tool_name=tool_name,
                )
            )
        return updated


class AwaitApprovalNode:
    async def __call__(
        self,
        state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState:
        request_id = state.get("purchase_request_id")
        if request_id is None:
            updated = state.copy()
            updated["status"] = "human_review"
            updated["review_reason"] = "Purchase request identity is missing before approval."
            return updated

        response = interrupt(
            {
                "request_id": str(request_id),
                "status": "pending_approval",
            },
            response_schema=ApprovalResume,
        )
        updated = state.copy()
        updated["approval_action"] = response["action"]
        updated["status"] = response["action"]
        return updated


class SubmitPurchaseRequestNode:
    def __init__(
        self,
        submitter: SubmitPurchaseRequest,
        observer: WorkflowObserver,
    ) -> None:
        self._submitter = submitter
        self._observer = observer

    async def __call__(
        self,
        state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState:
        request_id = state.get("purchase_request_id")
        if request_id is None:
            updated = state.copy()
            updated["status"] = "human_review"
            updated["review_reason"] = "Purchase request identity is missing before submission."
            return updated

        await self._submitter.execute(request_id)
        self._observer.record(
            WorkflowObservation(
                event="workflow_tool_completed",
                workflow_thread_id=state["workflow_id"],
                purchase_request_id=request_id,
                state_transition="submitted",
                tool_name="submit_order",
            )
        )
        updated = state.copy()
        updated["status"] = "submitted"
        updated["tool_results"] = (*state["tool_results"], "order_submitted")
        return updated
