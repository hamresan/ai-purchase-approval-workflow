from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import ManageDepartments
from ai_purchase_workflow.infrastructure.trusted_data.department_repository import (
    SqlAlchemyDepartmentRepository,
)
from ai_purchase_workflow.presentation.dependencies import get_session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def get_manage_departments(session: SessionDependency) -> ManageDepartments:
    return ManageDepartments(SqlAlchemyDepartmentRepository(session))
