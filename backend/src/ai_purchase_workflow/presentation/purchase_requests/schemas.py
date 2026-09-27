from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from ai_purchase_workflow.application.purchase_requests import (
    PurchaseRequestDetailView,
    PurchaseRequestView,
)
from ai_purchase_workflow.domain.purchase_requests import RequestStatus


class CreatePurchaseItemRequest(BaseModel):
    description: str
    quantity: int = Field(gt=0)
    unit_price_amount: Decimal = Field(ge=0)
    currency: str
    vendor: str | None = None


class CreatePurchaseRequestBody(BaseModel):
    requester_name: str | None = None
    items: list[CreatePurchaseItemRequest] = Field(min_length=1)


class EditPurchaseItemBody(BaseModel):
    description: str
    quantity: int = Field(gt=0)


class ApprovalBody(BaseModel):
    action: Literal["approve", "reject", "edit"]
    decided_by: str = Field(min_length=1)
    reason: str | None = None
    items: list[EditPurchaseItemBody] | None = None

    @model_validator(mode="after")
    def validate_action_payload(self) -> "ApprovalBody":
        if self.action == "reject" and (self.reason is None or not self.reason.strip()):
            raise ValueError("Rejected approval requests require a reason.")
        if self.action == "edit" and not self.items:
            raise ValueError("Edited approval requests require at least one item.")
        if self.action != "edit" and self.items is not None:
            raise ValueError("Items are accepted only for the edit approval action.")
        return self


class PurchaseItemResponse(BaseModel):
    description: str
    quantity: int
    unit_price_amount: Decimal
    currency: str
    vendor: str | None


class PurchaseRequestResponse(BaseModel):
    id: UUID
    requester_name: str | None
    items: list[PurchaseItemResponse]
    status: RequestStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_view(cls, view: PurchaseRequestView) -> "PurchaseRequestResponse":
        return cls(
            id=view.id,
            requester_name=view.requester_name,
            items=[
                PurchaseItemResponse(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price_amount=item.unit_price_amount,
                    currency=item.currency,
                    vendor=item.vendor,
                )
                for item in view.items
            ],
            status=view.status,
            created_at=view.created_at,
            updated_at=view.updated_at,
        )


class PurchaseRequestListResponse(BaseModel):
    items: list[PurchaseRequestResponse]
    total: int
    limit: int
    offset: int


class DraftOrderResponse(BaseModel):
    id: UUID
    items: list[PurchaseItemResponse]
    total_amount: Decimal
    currency: str
    created_at: datetime


class ApprovalDecisionResponse(BaseModel):
    outcome: str
    decided_by: str
    reason: str | None
    decided_at: datetime


class AuditEntryResponse(BaseModel):
    event_type: str
    message: str
    occurred_at: datetime


class PurchaseRequestDetailResponse(PurchaseRequestResponse):
    budget_outcome: Literal["passed", "not_checked"]
    draft_order: DraftOrderResponse | None
    approval_decision: ApprovalDecisionResponse | None
    audit_entries: list[AuditEntryResponse]

    @classmethod
    def from_detail_view(cls, view: PurchaseRequestDetailView) -> "PurchaseRequestDetailResponse":
        base = PurchaseRequestResponse.from_view(
            PurchaseRequestView(
                id=view.id,
                requester_name=view.requester_name,
                items=view.items,
                status=view.status,
                created_at=view.created_at,
                updated_at=view.updated_at,
            )
        )
        draft = view.draft_order
        decision = view.approval_decision
        return cls(
            **base.model_dump(),
            budget_outcome=view.budget_outcome,
            draft_order=None
            if draft is None
            else DraftOrderResponse(
                id=draft.id,
                items=[
                    PurchaseItemResponse(
                        description=item.description,
                        quantity=item.quantity,
                        unit_price_amount=item.unit_price_amount,
                        currency=item.currency,
                        vendor=item.vendor,
                    )
                    for item in draft.items
                ],
                total_amount=draft.total_amount,
                currency=draft.currency,
                created_at=draft.created_at,
            ),
            approval_decision=None
            if decision is None
            else ApprovalDecisionResponse(
                outcome=decision.outcome,
                decided_by=decision.decided_by,
                reason=decision.reason,
                decided_at=decision.decided_at,
            ),
            audit_entries=[
                AuditEntryResponse(
                    event_type=entry.event_type,
                    message=entry.message,
                    occurred_at=entry.occurred_at,
                )
                for entry in view.audit_entries
            ],
        )
