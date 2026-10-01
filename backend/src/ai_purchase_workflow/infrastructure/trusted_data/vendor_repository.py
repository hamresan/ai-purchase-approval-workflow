from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import VendorRecord, VendorRepository
from ai_purchase_workflow.infrastructure.trusted_data.models import VendorModel


class SqlAlchemyVendorRepository(VendorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_vendors(self) -> tuple[VendorRecord, ...]:
        result = await self._session.execute(select(VendorModel).order_by(VendorModel.name))
        return tuple(VendorRecord(row.id, row.name, row.is_active) for row in result.scalars())

    async def create_vendor(self, name: str) -> VendorRecord:
        row = VendorModel(id=uuid4(), name=name, is_active=True)
        self._session.add(row)
        await self._session.commit()
        return VendorRecord(row.id, row.name, row.is_active)

    async def update_vendor(
        self, vendor_id: UUID, name: str, is_active: bool
    ) -> VendorRecord | None:
        row = await self._session.get(VendorModel, vendor_id)
        if row is None:
            return None
        row.name = name
        row.is_active = is_active
        await self._session.commit()
        return VendorRecord(row.id, row.name, row.is_active)
