from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from ai_purchase_workflow.application.access import AuthorizationPolicy
from ai_purchase_workflow.application.admin import ManageDepartments
from ai_purchase_workflow.presentation.admin.dependencies import get_manage_departments
from ai_purchase_workflow.presentation.admin.mappers import AdminMapper
from ai_purchase_workflow.presentation.admin.schemas import (
    DepartmentCreateBody,
    DepartmentResponse,
    DepartmentUpdateBody,
)
from ai_purchase_workflow.presentation.auth import CurrentPrincipalDependency

router = APIRouter(prefix="/api/admin/departments", tags=["admin"])
ManageDepartmentsDependency = Annotated[ManageDepartments, Depends(get_manage_departments)]


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    manager: ManageDepartmentsDependency, principal: CurrentPrincipalDependency
) -> list[DepartmentResponse]:
    AuthorizationPolicy().require_admin(principal)
    return [AdminMapper.department_response(row) for row in await manager.list_departments()]


@router.post("", response_model=DepartmentResponse, status_code=201)
async def create_department(
    body: DepartmentCreateBody,
    manager: ManageDepartmentsDependency,
    principal: CurrentPrincipalDependency,
) -> DepartmentResponse:
    AuthorizationPolicy().require_admin(principal)
    try:
        record = await manager.create_department(body.name.strip())
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="Department name already exists.") from error
    return AdminMapper.department_response(record)


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: UUID,
    body: DepartmentUpdateBody,
    manager: ManageDepartmentsDependency,
    principal: CurrentPrincipalDependency,
) -> DepartmentResponse:
    AuthorizationPolicy().require_admin(principal)
    try:
        record = await manager.update_department(department_id, body.name.strip(), body.is_active)
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="Department name already exists.") from error
    if record is None:
        raise HTTPException(status_code=404, detail="Department not found.")
    return AdminMapper.department_response(record)
