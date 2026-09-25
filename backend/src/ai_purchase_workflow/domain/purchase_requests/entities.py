from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from ai_purchase_workflow.domain.purchase_requests.enums import ApprovalOutcome, RequestStatus
from ai_purchase_workflow.domain.purchase_requests.errors import (
    DomainValidationError,
    InvalidRequestTransitionError,
)
from ai_purchase_workflow.domain.purchase_requests.value_objects import Money, RequiredText

_ALLOWED_TRANSITIONS: dict[RequestStatus, frozenset[RequestStatus]] = {
    RequestStatus.DRAFTING: frozenset({RequestStatus.PENDING_APPROVAL, RequestStatus.FAILED}),
    RequestStatus.PENDING_APPROVAL: frozenset(
        {RequestStatus.APPROVED, RequestStatus.REJECTED, RequestStatus.FAILED}
    ),
    RequestStatus.APPROVED: frozenset({RequestStatus.SUBMITTED, RequestStatus.FAILED}),
    RequestStatus.REJECTED: frozenset(),
    RequestStatus.SUBMITTED: frozenset(),
    RequestStatus.FAILED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class PurchaseItem:
    description: str
    quantity: int
    unit_price: Money
    vendor: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "description", RequiredText(self.description, "Item description").value)
        if self.quantity <= 0:
            raise DomainValidationError("Item quantity must be greater than zero.")
        if self.vendor is not None:
            object.__setattr__(self, "vendor", RequiredText(self.vendor, "Vendor").value)

    @property
    def total_price(self) -> Money:
        return self.unit_price.multiply(self.quantity)


@dataclass(frozen=True, slots=True)
class DraftOrder:
    id: UUID
    request_id: UUID
    items: tuple[PurchaseItem, ...]
    total: Money
    created_at: datetime

    @classmethod
    def create(cls, request_id: UUID, items: tuple[PurchaseItem, ...], total: Money) -> "DraftOrder":
        if not items:
            raise DomainValidationError("A draft order must contain at least one item.")
        return cls(id=uuid4(), request_id=request_id, items=items, total=total, created_at=datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    id: UUID
    request_id: UUID
    outcome: ApprovalOutcome
    decided_by: str
    reason: str | None
    decided_at: datetime

    @classmethod
    def create(
        cls,
        request_id: UUID,
        outcome: ApprovalOutcome,
        decided_by: str,
        reason: str | None = None,
    ) -> "ApprovalDecision":
        normalized_reason = None if reason is None else RequiredText(reason, "Decision reason").value
        return cls(
            id=uuid4(),
            request_id=request_id,
            outcome=outcome,
            decided_by=RequiredText(decided_by, "Decided by").value,
            reason=normalized_reason,
            decided_at=datetime.now(UTC),
        )


@dataclass(frozen=True, slots=True)
class AuditEntry:
    id: UUID
    request_id: UUID
    event_type: str
    message: str
    occurred_at: datetime

    @classmethod
    def create(cls, request_id: UUID, event_type: str, message: str) -> "AuditEntry":
        return cls(
            id=uuid4(),
            request_id=request_id,
            event_type=RequiredText(event_type, "Audit event type").value,
            message=RequiredText(message, "Audit message").value,
            occurred_at=datetime.now(UTC),
        )


@dataclass(slots=True)
class PurchaseRequest:
    id: UUID
    requester_name: str | None
    items: tuple[PurchaseItem, ...]
    status: RequestStatus
    created_at: datetime
    updated_at: datetime
    draft_order: DraftOrder | None = None
    approval_decision: ApprovalDecision | None = None
    audit_entries: tuple[AuditEntry, ...] = field(default_factory=tuple)

    @classmethod
    def create(cls, items: tuple[PurchaseItem, ...], requester_name: str | None = None) -> "PurchaseRequest":
        if not items:
            raise DomainValidationError("A purchase request must contain at least one item.")
        normalized_requester = None
        if requester_name is not None:
            normalized_requester = RequiredText(requester_name, "Requester name").value
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            requester_name=normalized_requester,
            items=items,
            status=RequestStatus.DRAFTING,
            created_at=now,
            updated_at=now,
        )

    def transition_to(self, target_status: RequestStatus, *, occurred_at: datetime | None = None) -> None:
        if target_status not in _ALLOWED_TRANSITIONS[self.status]:
            raise InvalidRequestTransitionError(self.status.value, target_status.value)
        self.status = target_status
        self.updated_at = occurred_at or datetime.now(UTC)
