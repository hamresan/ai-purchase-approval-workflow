# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
from typing import cast

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from ai_purchase_workflow.infrastructure.workflows.nodes import (
    AwaitApprovalNode,
    ExtractPurchaseRequestNode,
    PreparePurchaseRequestNode,
    SubmitPurchaseRequestNode,
)
from ai_purchase_workflow.infrastructure.workflows.routing import (
    route_after_approval,
    route_after_extraction,
)
from ai_purchase_workflow.infrastructure.workflows.state import PurchaseRequestWorkflowState


class PurchaseRequestWorkflow:
    def __init__(
        self,
        extract_node: ExtractPurchaseRequestNode,
        prepare_node: PreparePurchaseRequestNode,
        await_approval_node: AwaitApprovalNode,
        submit_node: SubmitPurchaseRequestNode,
        checkpointer: BaseCheckpointSaver,
    ) -> None:
        builder = StateGraph(PurchaseRequestWorkflowState)
        builder.add_node("extract", extract_node)
        builder.add_node("prepare", prepare_node)
        builder.add_node("await_approval", await_approval_node)
        builder.add_node("submit", submit_node)
        builder.add_edge(START, "extract")
        builder.add_conditional_edges(
            "extract",
            route_after_extraction,
            {"prepare": "prepare", "human_review": END},
        )
        builder.add_edge("prepare", "await_approval")
        builder.add_conditional_edges(
            "await_approval",
            route_after_approval,
            {"submit": "submit", "rejected": END, "human_review": END},
        )
        builder.add_edge("submit", END)
        self.graph = builder.compile(checkpointer=checkpointer)

    async def execute(
        self,
        state: PurchaseRequestWorkflowState,
        *,
        thread_id: str,
    ) -> PurchaseRequestWorkflowState:
        raw_state = await self.graph.ainvoke(
            state,
            config={"configurable": {"thread_id": thread_id}},
        )
        return cast(PurchaseRequestWorkflowState, raw_state)

    async def resume(
        self,
        *,
        thread_id: str,
        action: str,
    ) -> PurchaseRequestWorkflowState:
        raw_state = await self.graph.ainvoke(
            Command(resume={"action": action}),
            config={"configurable": {"thread_id": thread_id}},
        )
        return cast(PurchaseRequestWorkflowState, raw_state)
