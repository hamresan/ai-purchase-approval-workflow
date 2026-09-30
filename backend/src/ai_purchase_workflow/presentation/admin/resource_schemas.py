from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from ai_purchase_workflow.application.access import ApplicationRole


class NamedResourceBody(BaseModel):
    id: UUID
    name: str = Field(min_length=1, max_length=200)
    is_active: bool = True


class OfferBody(BaseModel):
    id: UUID
    product_id: UUID
    vendor_id: UUID
    unit_price_amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    available_quantity: int = Field(ge=0)
    is_active: bool = True


class BudgetBody(BaseModel):
    id: UUID
    owner_type: Literal["USER", "DEPARTMENT"]
    user_id: UUID | None = None
    department_id: UUID | None = None
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    is_active: bool = True


class RoleAssignmentBody(BaseModel):
    roles: set[ApplicationRole]
