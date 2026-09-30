from uuid import UUID

import pytest

from ai_purchase_workflow.application.admin import DepartmentRecord, ManageDepartments
from tests.unit.application.admin.fake_department_repository import FakeDepartmentRepository




@pytest.mark.asyncio
async def test_department_management_delegates_to_repository() -> None:
    repository = FakeDepartmentRepository()
    manager = ManageDepartments(repository)
    created = await manager.create_department("Engineering")
    assert await manager.list_departments() == (created,)
    updated = await manager.update_department(created.id, "Operations", False)
    assert updated == DepartmentRecord(created.id, "Operations", False)
    assert await manager.update_department(UUID(int=2), "Missing", False) is None
