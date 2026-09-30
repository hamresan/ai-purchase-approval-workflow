from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import (
    AdminResourceRepository,
    BudgetRecord,
    OfferRecord,
    ProductRecord,
    VendorRecord,
)
from ai_purchase_workflow.infrastructure.trusted_data.admin_resource_mapper import AdminResourceMapper
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
        rows = (await self._session.execute(select(ProductModel).order_by(ProductModel.name))).scalars()
        return tuple(AdminResourceMapper.product(row) for row in rows)

    async def save_product(self, record: ProductRecord) -> ProductRecord:
        await self._session.merge(AdminResourceMapper.product_model(record))
        await self._session.commit()
        return record

    async def list_vendors(self) -> tuple[VendorRecord, ...]:
        rows = (await self._session.execute(select(VendorModel).order_by(VendorModel.name))).scalars()
        return tuple(AdminResourceMapper.vendor(row) for row in rows)

    async def save_vendor(self, record: VendorRecord) -> VendorRecord:
        await self._session.merge(AdminResourceMapper.vendor_model(record))
        await self._session.commit()
        return record

    async def list_offers(self) -> tuple[OfferRecord, ...]:
        rows = (await self._session.execute(select(TrustedOfferModel))).scalars()
        return tuple(AdminResourceMapper.offer(row) for row in rows)

    async def save_offer(self, record: OfferRecord) -> OfferRecord:
        await self._session.merge(AdminResourceMapper.offer_model(record))
        await self._session.commit()
        return record

    async def list_budgets(self) -> tuple[BudgetRecord, ...]:
        rows = (await self._session.execute(select(BudgetLimitModel))).scalars()
        return tuple(AdminResourceMapper.budget(row) for row in rows)

    async def save_budget(self, record: BudgetRecord) -> BudgetRecord:
        await self._session.merge(AdminResourceMapper.budget_model(record))
        await self._session.commit()
        return record
