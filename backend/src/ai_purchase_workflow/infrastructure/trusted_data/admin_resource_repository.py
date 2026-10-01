from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import (
    AdminResourceRepository,
    BudgetRecord,
    OfferRecord,
    ProductRecord,
    VendorRecord,
)
from ai_purchase_workflow.infrastructure.trusted_data.admin_resource_mapper import (
    AdminResourceMapper,
)
from ai_purchase_workflow.infrastructure.trusted_data.models import (
    BudgetLimitModel,
    ProductModel,
    TrustedOfferModel,
    VendorModel,
)


class SqlAlchemyAdminResourceRepository(AdminResourceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_products(self) -> tuple[ProductRecord, ...]:
        result = await self._session.execute(select(ProductModel).order_by(ProductModel.name))
        return tuple(AdminResourceMapper.product(row) for row in result.scalars())

    async def save_product(self, record: ProductRecord) -> ProductRecord:
        await self._session.merge(AdminResourceMapper.product_model(record))
        await self._session.commit()
        return record

    async def list_vendors(self) -> tuple[VendorRecord, ...]:
        result = await self._session.execute(select(VendorModel).order_by(VendorModel.name))
        return tuple(AdminResourceMapper.vendor(row) for row in result.scalars())

    async def save_vendor(self, record: VendorRecord) -> VendorRecord:
        await self._session.merge(AdminResourceMapper.vendor_model(record))
        await self._session.commit()
        return record

    async def list_offers(self) -> tuple[OfferRecord, ...]:
        result = await self._session.execute(select(TrustedOfferModel))
        return tuple(AdminResourceMapper.offer(row) for row in result.scalars())

    async def save_offer(self, record: OfferRecord) -> OfferRecord:
        await self._session.merge(AdminResourceMapper.offer_model(record))
        await self._session.commit()
        return record

    async def list_budgets(self) -> tuple[BudgetRecord, ...]:
        result = await self._session.execute(select(BudgetLimitModel))
        return tuple(AdminResourceMapper.budget(row) for row in result.scalars())

    async def save_budget(self, record: BudgetRecord) -> BudgetRecord:
        await self._session.merge(AdminResourceMapper.budget_model(record))
        await self._session.commit()
        return record
