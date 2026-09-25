# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict, cast
from uuid import UUID, uuid4

from langgraph.graph import END, START, StateGraph

from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractedPurchaseRequest,
    ExtractPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.preparation import (
    PrepareExtractedPurchaseRequest,
)

WorkflowStatus = Literal["started", "extracted", "human_review", "pending_approval"]


class PurchaseRequestWorkflowState(TypedDict):
    workflow_id: str
    messages: tuple[str, ...]
    free_text: str
    status: WorkflowStatus
    tool_results: tuple[str, ...]
    extracted_request: NotRequired[ExtractedPurchaseRequest]
    purchase_request_id: NotRequired[UUID]
    review_reason: NotRequired[str]


@dataclass(frozen=True, slots=True)
class PurchaseRequestWorkflowResult:
    workflow_id: str
    purchase_request_id: UUID | None
    status: WorkflowStatus
    needs_human_review: bool
    review_reason: str | None
    tool_results: tuple[str, ...]


class PurchaseRequestWorkflow:
    def __init__(
        self,
        extractor: ExtractPurchaseRequest,
        preparer: PrepareExtractedPurchaseRequest,
    ) -> None:
        self._extractor = extractor
        self._preparer = preparer
        builder = StateGraph(PurchaseRequestWorkflowState)
        builder.add_node("extract", self._extract)
        builder.add_node("prepare", self._prepare)
        builder.add_edge(START, "extract")
        builder.add_conditional_edges(
            "extract",
            self._route_after_extraction,
            {"prepare": "prepare", "human_review": END},
        )
        builder.add_edge("prepare", END)
        self._graph = builder.compile()

    async def execute(
        self,
        free_text: str,
        *,
        checkpoint_id: str | None = None,
    ) -> PurchaseRequestWorkflowResult:
        initial_state: PurchaseRequestWorkflowState = {
            "workflow_id": checkpoint_id or str(uuid4()),
            "messages": (free_text,),
            "free_text": free_text,
            "status": "started",
            "tool_results": (),
        }
        raw_state = await self._graph.ainvoke(initial_state)
        state = cast(PurchaseRequestWorkflowState, raw_state)
        return PurchaseRequestWorkflowResult(
            checkpoint_id=state["workflow_id"],
            purchase_request_id=state.get("purchase_request_id"),
            status=state["status"],
            needs_human_review=state["status"] == "human_review",
            review_reason=state.get("review_reason"),
            tool_results=state["tool_results"],
        )

    async def _extract(self, state: PurchaseRequestWorkflowState) -> PurchaseRequestWorkflowState:
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

    async def _prepare(self, state: PurchaseRequestWorkflowState) -> PurchaseRequestWorkflowState:
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

    @staticmethod
    def _route_after_extraction(
        state: PurchaseRequestWorkflowState,
    ) -> Literal["prepare", "human_review"]:
        if state["status"] == "human_review":
            return "human_review"
        return "prepare"
