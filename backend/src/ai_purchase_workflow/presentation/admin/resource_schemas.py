from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from ai_purchase_workflow.application.access import ApplicationRole

class NamedResourceCreateBody(BaseModel):
    name: str = Field(min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Name must not be blank.")
        return stripped


class NamedResourceUpdateBody(NamedResourceCreateBody):
    is_active: bool


class CurrencyBody(BaseModel):
    currency: str = Field(min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("Currency must be a three-letter alphabetic code.")
        return normalized


class OfferBody(CurrencyBody):
    product_id: UUID
    vendor_id: UUID
    unit_price_amount: Decimal = Field(gt=0)
    available_quantity: int = Field(ge=0)
    is_active: bool = True


class BudgetBody(CurrencyBody):
    owner_type: Literal["USER", "DEPARTMENT"]
    user_id: UUID | None = None
    department_id: UUID | None = None
    amount: Decimal = Field(gt=0)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_owner(self) -> "BudgetBody":
        user_owner = (
            self.owner_type == "USER" and self.user_id is not None and self.department_id is None
        )
        department_owner = (
            self.owner_type == "DEPARTMENT"
            and self.department_id is not None
            and self.user_id is None
        )
        if not (user_owner or department_owner):
            raise ValueError("Budget owner identifier must match owner_type.")
        return self


class RoleAssignmentBody(BaseModel):
    roles: set[ApplicationRole]


class RoleAssignmentResponse(BaseModel):
    user_id: UUID
    roles: set[ApplicationRole]


class ProductResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool


class VendorResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool


class OfferResponse(BaseModel):
    id: UUID
    product_id: UUID
    vendor_id: UUID
    unit_price_amount: str
    currency: str
    available_quantity: int
    is_active: bool


class BudgetResponse(BaseModel):
    id: UUID
    owner_type: str
    user_id: UUID | None
    department_id: UUID | None
    amount: str
    currency: str
    is_active: bool
