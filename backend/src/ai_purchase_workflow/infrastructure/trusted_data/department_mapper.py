from ai_purchase_workflow.application.admin import DepartmentRecord
from ai_purchase_workflow.infrastructure.trusted_data.models import DepartmentModel


class DepartmentMapper:
    @staticmethod
    def to_record(row: DepartmentModel) -> DepartmentRecord:
        return DepartmentRecord(id=row.id, name=row.name, is_active=row.is_active)
