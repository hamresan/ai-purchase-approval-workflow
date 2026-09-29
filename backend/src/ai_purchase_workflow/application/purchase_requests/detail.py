from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.dto import PurchaseItemView
from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.application.purchase_requests.use_cases import (
    PurchaseRequestNotFoundError,
)
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus


@dataclass(frozen=True, slots=True)
class DraftOrderView:
    id: UUID
    items: tuple[PurchaseItemView, ...]
    total_amount: Decimal
    currency: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ApprovalDecisionView:
    outcome: str
    decided_by: str
    reason: str | None
    decided_at: datetime


@dataclass(frozen=True, slots=True)
class AuditEntryView:
    event_type: str
    message: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PurchaseRequestDetailView:
    id: UUID
    requester_name: str | None
    items: tuple[PurchaseItemView, ...]
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    budget_outcome: Literal["passed", "not_checked"]
    draft_order: DraftOrderView | None
    approval_decision: ApprovalDecisionView | None
    audit_entries: tuple[AuditEntryView, ...]
    requester_user_id: UUID | None = None

    @classmethod
    def from_domain(cls, request: PurchaseRequest) -> "PurchaseRequestDetailView":
        draft = request.draft_order
        decision = request.approval_decision
        budget_outcome = (
            "passed"
            if any(entry.event_type == "trusted_data_validated" for entry in request.audit_entries)
            else "not_checked"
        )
        return cls(
            id=request.id,
            requester_name=request.requester_name,
            items=tuple(
                PurchaseItemView(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price_amount=item.unit_price.amount,
                    currency=item.unit_price.currency,
                    vendor=item.vendor,
                )
                for item in request.items
            ),
            status=request.status,
            created_at=request.created_at,
            updated_at=request.updated_at,
            budget_outcome=budget_outcome,
            draft_order=None
            if draft is None
            else DraftOrderView(
                id=draft.id,
                items=tuple(
                    PurchaseItemView(
                        description=item.description,
                        quantity=item.quantity,
                        unit_price_amount=item.unit_price.amount,
                        currency=item.unit_price.currency,
                        vendor=item.vendor,
                    )
                    for item in draft.items
                ),
                total_amount=draft.total.amount,
                currency=draft.total.currency,
                created_at=draft.created_at,
            ),
            approval_decision=None
            if decision is None
            else ApprovalDecisionView(
                outcome=decision.outcome.value,
                decided_by=decision.decided_by,
                reason=decision.reason,
                decided_at=decision.decided_at,
            ),
            requester_user_id=request.requester_user_id,
            audit_entries=tuple(
                AuditEntryView(entry.event_type, entry.message, entry.occurred_at)
                for entry in request.audit_entries
            ),
        )


class GetPurchaseRequestDetail:
    def __init__(self, repository: PurchaseRequestRepository) -> None:
        self._repository = repository

    async def execute(self, request_id: UUID) -> PurchaseRequestDetailView:
        request = await self._repository.get(request_id)
        if request is None:
            raise PurchaseRequestNotFoundError(request_id)
        return PurchaseRequestDetailView.from_domain(request)
