from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import ProductRecord, ProductRepository
from ai_purchase_workflow.infrastructure.trusted_data.models import ProductModel


class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_products(self) -> tuple[ProductRecord, ...]:
        result = await self._session.execute(select(ProductModel).order_by(ProductModel.name))
        return tuple(ProductRecord(row.id, row.name, row.is_active) for row in result.scalars())

    async def create_product(self, name: str) -> ProductRecord:
        row = ProductModel(id=uuid4(), name=name, is_active=True)
        self._session.add(row)
        await self._session.commit()
        return ProductRecord(row.id, row.name, row.is_active)

    async def update_product(\n        self, product_id: UUID, name: str, is_active: bool\n    ) -> ProductRecord | None:
        row = await self._session.get(ProductModel, product_id)
        if row is None:
            return None
        row.name = name
        row.is_active = is_active
        await self._session.commit()
        return ProductRecord(row.id, row.name, row.is_active)
