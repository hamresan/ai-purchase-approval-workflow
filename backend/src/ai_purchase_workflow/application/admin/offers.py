from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID


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
class OfferValues:
    product_id: UUID
    vendor_id: UUID
    unit_price_amount: Decimal
    currency: str
    available_quantity: int
    is_active: bool


class OfferRepository(Protocol):
    async def list_offers(self) -> tuple[OfferRecord, ...]: ...
    async def create_offer(self, values: OfferValues) -> OfferRecord: ...
    async def update_offer(self, offer_id: UUID, values: OfferValues) -> OfferRecord | None: ...


class ManageOffers:
    def __init__(self, repository: OfferRepository) -> None:
        self._repository = repository

    async def list_offers(self) -> tuple[OfferRecord, ...]:
        return await self._repository.list_offers()

    async def create_offer(self, values: OfferValues) -> OfferRecord:
        return await self._repository.create_offer(values)

    async def update_offer(self, offer_id: UUID, values: OfferValues) -> OfferRecord | None:
        return await self._repository.update_offer(offer_id, values)
