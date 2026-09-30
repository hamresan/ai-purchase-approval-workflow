from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ProductRecord:
    id: UUID
    name: str
    is_active: bool


@dataclass(frozen=True, slots=True)
class VendorRecord:
    id: UUID
    name: str
    is_active: bool


@dataclass(frozen=True, slots=True)
class OfferRecord:
    id: UUID
    product_id: UUID
    vendor_id: UUID
    unit_price_amount: Decimal
    currency: str
    available_quantity: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class BudgetRecord:
    id: UUID
    owner_type: Literal["USER", "DEPARTMENT"]
    user_id: UUID | None
    department_id: UUID | None
    amount: Decimal
    currency: str
    is_active: bool


class AdminResourceRepository(Protocol):
    async def list_products(self) -> tuple[ProductRecord, ...]: ...
    async def save_product(self, record: ProductRecord) -> ProductRecord: ...
    async def list_vendors(self) -> tuple[VendorRecord, ...]: ...
    async def save_vendor(self, record: VendorRecord) -> VendorRecord: ...
    async def list_offers(self) -> tuple[OfferRecord, ...]: ...
    async def save_offer(self, record: OfferRecord) -> OfferRecord: ...
    async def list_budgets(self) -> tuple[BudgetRecord, ...]: ...
    async def save_budget(self, record: BudgetRecord) -> BudgetRecord: ...
