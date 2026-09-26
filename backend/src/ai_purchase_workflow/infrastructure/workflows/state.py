from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict
from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractedPurchaseRequest,
)

WorkflowStatus = Literal[
    "started",
    "extracted",
    "human_review",
    "pending_approval",
    "approved",
    "rejected",
    "submitted",
]


class ApprovalResume(TypedDict):
    action: Literal["approved", "rejected"]


class PurchaseRequestWorkflowState(TypedDict):
    workflow_id: str
    messages: tuple[str, ...]
    free_text: str
    status: WorkflowStatus
    tool_results: tuple[str, ...]
    extracted_request: NotRequired[ExtractedPurchaseRequest]
    purchase_request_id: NotRequired[UUID]
    review_reason: NotRequired[str]
    approval_action: NotRequired[Literal["approved", "rejected"]]


@dataclass(frozen=True, slots=True)
class PurchaseRequestWorkflowResult:
    checkpoint_id: str
    purchase_request_id: UUID | None
    status: WorkflowStatus
    needs_human_review: bool
    review_reason: str | None
    tool_results: tuple[str, ...]
