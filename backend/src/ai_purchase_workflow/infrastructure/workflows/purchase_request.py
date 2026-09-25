# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
from typing import cast

from langgraph.graph import END, START, StateGraph

from ai_purchase_workflow.infrastructure.workflows.nodes import (
    ExtractPurchaseRequestNode,
    PreparePurchaseRequestNode,
)
from ai_purchase_workflow.infrastructure.workflows.routing import route_after_extraction
from ai_purchase_workflow.infrastructure.workflows.state import PurchaseRequestWorkflowState


class PurchaseRequestWorkflow:
    def __init__(
        self,
        extract_node: ExtractPurchaseRequestNode,
        prepare_node: PreparePurchaseRequestNode,
    ) -> None:
        builder = StateGraph(PurchaseRequestWorkflowState)
        builder.add_node("extract", extract_node)
        builder.add_node("prepare", prepare_node)
        builder.add_edge(START, "extract")
        builder.add_conditional_edges(
            "extract",
            route_after_extraction,
            {"prepare": "prepare", "human_review": END},
        )
        builder.add_edge("prepare", END)
        self.graph = builder.compile()

    async def execute(self, state: PurchaseRequestWorkflowState) -> PurchaseRequestWorkflowState:
        raw_state = await self.graph.ainvoke(state)
        return cast(PurchaseRequestWorkflowState, raw_state)
