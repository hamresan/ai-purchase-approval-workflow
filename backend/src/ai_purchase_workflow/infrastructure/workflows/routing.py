from typing import Literal

from ai_purchase_workflow.infrastructure.workflows.state import (
    PurchaseRequestWorkflowState,
)


def route_after_extraction(
    state: PurchaseRequestWorkflowState,
) -> Literal["prepare", "human_review"]:
    if state["status"] == "human_review":
        return "human_review"
    return "prepare"
