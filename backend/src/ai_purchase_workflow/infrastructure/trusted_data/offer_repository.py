from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import OfferRecord, OfferRepository, OfferValues
from ai_purchase_workflow.infrastructure.trusted_data.models import TrustedOfferModel


def _record(row: TrustedOfferModel) -> OfferRecord:
    return OfferRecord(row.id, row.product_id, row.vendor_id, row.unit_price_amount, row.currency, row.available_quantity, row.is_active)


def _apply(row: TrustedOfferModel, values: OfferValues) -> None:
    row.product_id = values.product_id
    row.vendor_id = values.vendor_id
    row.unit_price_amount = values.unit_price_amount
    row.currency = values.currency
    row.available_quantity = values.available_quantity
    row.is_active = values.is_active


class SqlAlchemyOfferRepository(OfferRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_offers(self) -> tuple[OfferRecord, ...]:
        result = await self._session.execute(select(TrustedOfferModel))
        return tuple(_record(row) for row in result.scalars())

    async def create_offer(self, values: OfferValues) -> OfferRecord:
        row = TrustedOfferModel(id=uuid4(), product_id=values.product_id, vendor_id=values.vendor_id, unit_price_amount=values.unit_price_amount, currency=values.currency, available_quantity=values.available_quantity, is_active=values.is_active)
        self._session.add(row)
        await self._session.commit()
        return _record(row)

    async def update_offer(self, offer_id: UUID, values: OfferValues) -> OfferRecord | None:
        row = await self._session.get(TrustedOfferModel, offer_id)
        if row is None:
            return None
        _apply(row, values)
        await self._session.commit()
        return _record(row)
