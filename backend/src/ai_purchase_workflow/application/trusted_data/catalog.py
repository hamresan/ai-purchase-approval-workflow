from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.domain.purchase_requests import Money


@dataclass(frozen=True, slots=True)
class TrustedCatalogItem:
    product_id: UUID
    description: str
    vendor_id: UUID
    vendor_name: str
    unit_price: Money
    available_quantity: int


class TrustedCatalogReader(Protocol):
    async def find_item(self, description: str) -> TrustedCatalogItem: ...
