from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import DepartmentRecord, DepartmentRepository
from ai_purchase_workflow.infrastructure.trusted_data.department_mapper import DepartmentMapper
from ai_purchase_workflow.infrastructure.trusted_data.models import DepartmentModel


class SqlAlchemyDepartmentRepository(DepartmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_departments(self) -> tuple[DepartmentRecord, ...]:
        rows = (await self._session.execute(
            select(DepartmentModel).order_by(DepartmentModel.name)
        )).scalars().all()
        return tuple(DepartmentMapper.to_record(row) for row in rows)

    async def create_department(self, name: str) -> DepartmentRecord:
        row = DepartmentModel(id=uuid4(), name=name, is_active=True)
        self._session.add(row)
        await self._session.commit()
        return DepartmentMapper.to_record(row)

    async def update_department(
        self, department_id: UUID, name: str, is_active: bool
    ) -> DepartmentRecord | None:
        row = await self._session.get(DepartmentModel, department_id)
        if row is None:
            return None
        row.name = name
        row.is_active = is_active
        await self._session.commit()
        return DepartmentMapper.to_record(row)
