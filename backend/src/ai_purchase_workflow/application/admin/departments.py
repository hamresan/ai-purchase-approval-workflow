from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DepartmentRecord:
    id: UUID
    name: str
    is_active: bool


class DepartmentRepository(Protocol):
    async def list_departments(self) -> tuple[DepartmentRecord, ...]: ...
    async def create_department(self, name: str) -> DepartmentRecord: ...
    async def update_department(
        self, department_id: UUID, name: str, is_active: bool
    ) -> DepartmentRecord | None: ...


class ManageDepartments:
    def __init__(self, repository: DepartmentRepository) -> None:
        self._repository = repository

    async def list_departments(self) -> tuple[DepartmentRecord, ...]:
        return await self._repository.list_departments()

    async def create_department(self, name: str) -> DepartmentRecord:
        return await self._repository.create_department(name)

    async def update_department(
        self, department_id: UUID, name: str, is_active: bool
    ) -> DepartmentRecord | None:
        return await self._repository.update_department(department_id, name, is_active)
