from uuid import UUID

from ai_purchase_workflow.application.admin import DepartmentRecord, DepartmentRepository


class FakeDepartmentRepository(DepartmentRepository):
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
