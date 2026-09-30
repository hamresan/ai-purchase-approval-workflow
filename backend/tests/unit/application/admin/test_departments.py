from uuid import UUID

import pytest

from ai_purchase_workflow.application.admin import DepartmentRecord, ManageDepartments


class FakeDepartmentRepository:
    def __init__(self) -> None:
        self.rows: dict[UUID, DepartmentRecord] = {}

    async def list_departments(self) -> tuple[DepartmentRecord, ...]:
        return tuple(self.rows.values())

    async def create_department(self, name: str) -> DepartmentRecord:
        record = DepartmentRecord(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"), name, True)
        self.rows[record.id] = record
        return record

    async def update_department(
        self, department_id: UUID, name: str, is_active: bool
    ) -> DepartmentRecord | None:
        if department_id not in self.rows:
            return None
        record = DepartmentRecord(department_id, name, is_active)
        self.rows[department_id] = record
        return record


@pytest.mark.asyncio
async def test_department_management_delegates_to_repository() -> None:
    repository = FakeDepartmentRepository()
    manager = ManageDepartments(repository)
    created = await manager.create_department("Engineering")
    assert await manager.list_departments() == (created,)
    updated = await manager.update_department(created.id, "Operations", False)
    assert updated == DepartmentRecord(created.id, "Operations", False)
    assert await manager.update_department(UUID(int=2), "Missing", False) is None
