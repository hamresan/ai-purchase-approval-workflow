from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ai_purchase_workflow.application.admin import DepartmentRecord


class DepartmentCreateBody(BaseModel):
    name: str = Field(min_length=1, max_length=160)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Department name must not be blank.")
        return stripped


class DepartmentUpdateBody(DepartmentCreateBody):
    is_active: bool


class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool

    @classmethod
    def from_record(cls, record: DepartmentRecord) -> "DepartmentResponse":
        return cls(id=record.id, name=record.name, is_active=record.is_active)
