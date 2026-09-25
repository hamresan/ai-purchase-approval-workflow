# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
from typing import cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.preparation import (
    PrepareExtractedPurchaseRequest,
)
from ai_purchase_workflow.infrastructure.workflows.nodes import (
    ExtractPurchaseRequestNode,
    PreparePurchaseRequestNode,
)
from ai_purchase_workflow.infrastructure.workflows.routing import route_after_extraction
from ai_purchase_workflow.infrastructure.workflows.state import (
    PurchaseRequestWorkflowResult,
    PurchaseRequestWorkflowState,
)


class PurchaseRequestWorkflow:
    def __init__(
        self,
        extractor: ExtractPurchaseRequest,
        preparer: PrepareExtractedPurchaseRequest,
    ) -> None:
        builder = StateGraph(PurchaseRequestWorkflowState)
        builder.add_node("extract", ExtractPurchaseRequestNode(extractor))
        builder.add_node("prepare", PreparePurchaseRequestNode(preparer))
        builder.add_edge(START, "extract")
        builder.add_conditional_edges(
            "extract",
            route_after_extraction,
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
