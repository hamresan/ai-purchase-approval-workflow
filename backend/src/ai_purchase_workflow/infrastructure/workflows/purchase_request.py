from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID, uuid4

from langgraph.graph import END, START, StateGraph

from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractPurchaseRequest,
    ExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.preparation import (
    PrepareExtractedPurchaseRequest,
)


class PurchaseRequestWorkflowState(TypedDict, total=False):
    checkpoint_id: str
    messages: tuple[str, ...]
    free_text: str
    extracted_request: ExtractedPurchaseRequest
    purchase_request_id: UUID
    status: str
    tool_results: tuple[str, ...]
    review_reason: str


@dataclass(frozen=True, slots=True)
class PurchaseRequestWorkflowResult:
    checkpoint_id: str
    purchase_request_id: UUID | None
    status: str
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
            "checkpoint_id": checkpoint_id or str(uuid4()),
            "messages": (free_text,),
            "free_text": free_text,
            "tool_results": (),
        }
        state = await self._graph.ainvoke(initial_state)
        return PurchaseRequestWorkflowResult(
            checkpoint_id=state["checkpoint_id"],
            purchase_request_id=state.get("purchase_request_id"),
            status=state["status"],
            needs_human_review=state["status"] == "human_review",
            review_reason=state.get("review_reason"),
            tool_results=state.get("tool_results", ()),
        )

    async def _extract(
        self, state: PurchaseRequestWorkflowState
    ) -> PurchaseRequestWorkflowState:
        outcome = await self._extractor.execute(state["free_text"])
        if outcome.needs_human_review or outcome.extracted_request is None:
            return {
                "status": "human_review",
                "review_reason": outcome.review_reason or "Extraction requires human review.",
            }
        return {
            "extracted_request": outcome.extracted_request,
            "status": "extracted",
        }

    async def _prepare(
        self, state: PurchaseRequestWorkflowState
    ) -> PurchaseRequestWorkflowState:
        try:
            request = await self._preparer.execute(state["extracted_request"])
        except Exception as error:
            return {
                "status": "human_review",
                "review_reason": f"Trusted tool execution failed: {error}",
                "tool_results": ("prepare_failed",),
            }
        return {
            "purchase_request_id": request.id,
            "status": "pending_approval",
            "tool_results": ("trusted_data_resolved", "draft_order_created", "budget_checked"),
        }

    @staticmethod
    def _route_after_extraction(state: PurchaseRequestWorkflowState) -> str:
        if state["status"] == "human_review":
            return "human_review"
        return "prepare"
