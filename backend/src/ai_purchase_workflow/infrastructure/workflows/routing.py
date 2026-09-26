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


def route_after_preparation(
    state: PurchaseRequestWorkflowState,
) -> Literal["await_approval", "human_review"]:
    if state["status"] == "pending_approval":
        return "await_approval"
    return "human_review"


def route_after_approval(
    state: PurchaseRequestWorkflowState,
) -> Literal["submit", "rejected", "human_review"]:
    if state["status"] == "approved":
        return "submit"
    if state["status"] == "rejected":
        return "rejected"
    return "human_review"
