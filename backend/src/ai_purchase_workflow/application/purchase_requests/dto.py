from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus


@dataclass(frozen=True, slots=True)
class CreatePurchaseItem:
    description: str
    quantity: int
    unit_price_amount: Decimal
    currency: str
    vendor: str | None = None


@dataclass(frozen=True, slots=True)
class CreatePurchaseRequestCommand:
    requester_name: str | None
    items: tuple[CreatePurchaseItem, ...]


@dataclass(frozen=True, slots=True)
class PurchaseRequestListQuery:
    status: RequestStatus | None = None
    limit: int = 20
    offset: int = 0
    descending: bool = True


@dataclass(frozen=True, slots=True)
class PurchaseRequestView:
    id: UUID
    requester_name: str | None
    items: tuple[CreatePurchaseItem, ...]
    status: RequestStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, request: PurchaseRequest) -> "PurchaseRequestView":
        return cls(
            id=request.id,
            requester_name=request.requester_name,
            items=tuple(
                CreatePurchaseItem(
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
        )


@dataclass(frozen=True, slots=True)
class PurchaseRequestPage:
    items: tuple[PurchaseRequestView, ...]
    total: int
    limit: int
    offset: int
