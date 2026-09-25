from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from ai_purchase_workflow.application.purchase_requests import PurchaseRequestView
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
