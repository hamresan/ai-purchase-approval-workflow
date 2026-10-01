from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.access import ApplicationPrincipal, AuthorizationPolicy
from ai_purchase_workflow.application.admin import (
    BudgetRecord,
    OfferRecord,
    ProductRecord,
    VendorRecord,
)
from ai_purchase_workflow.infrastructure.access.sqlalchemy_role_assignment_repository import (
    SqlAlchemyRoleAssignmentRepository,
)
from ai_purchase_workflow.infrastructure.trusted_data.admin_resource_repository import (
    SqlAlchemyAdminResourceRepository,
)
from ai_purchase_workflow.presentation.admin.resource_schemas import (
    BudgetBody,
    NamedResourceBody,
    OfferBody,
    RoleAssignmentBody,
)
from ai_purchase_workflow.presentation.auth import CurrentPrincipalDependency
from ai_purchase_workflow.presentation.dependencies import get_session

router = APIRouter(prefix="/api/admin", tags=["admin-resources"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def _authorize(principal: ApplicationPrincipal) -> None:
    AuthorizationPolicy().require_admin(principal)


@router.get("/products")
async def list_products(
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    return await SqlAlchemyAdminResourceRepository(session).list_products()


@router.put("/products/{resource_id}")
async def save_product(
    resource_id: UUID,
    body: NamedResourceBody,
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    record = ProductRecord(resource_id, body.name.strip(), body.is_active)
    return await SqlAlchemyAdminResourceRepository(session).save_product(record)


@router.get("/vendors")
async def list_vendors(
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    return await SqlAlchemyAdminResourceRepository(session).list_vendors()


@router.put("/vendors/{resource_id}")
async def save_vendor(
    resource_id: UUID,
    body: NamedResourceBody,
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    record = VendorRecord(resource_id, body.name.strip(), body.is_active)
    return await SqlAlchemyAdminResourceRepository(session).save_vendor(record)


@router.get("/offers")
async def list_offers(
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    return await SqlAlchemyAdminResourceRepository(session).list_offers()


@router.put("/offers/{resource_id}")
async def save_offer(
    resource_id: UUID,
    body: OfferBody,
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    record = OfferRecord(
        resource_id,
        body.product_id,
        body.vendor_id,
        body.unit_price_amount,
        body.currency.upper(),
        body.available_quantity,
        body.is_active,
    )
    return await SqlAlchemyAdminResourceRepository(session).save_offer(record)


@router.get("/budgets")
async def list_budgets(
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    return await SqlAlchemyAdminResourceRepository(session).list_budgets()


@router.put("/budgets/{resource_id}")
async def save_budget(
    resource_id: UUID,
    body: BudgetBody,
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    record = BudgetRecord(
        resource_id,
        body.owner_type,
        body.user_id,
        body.department_id,
        body.amount,
        body.currency.upper(),
        body.is_active,
    )
    return await SqlAlchemyAdminResourceRepository(session).save_budget(record)


@router.get("/roles")
async def list_roles(
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    return await SqlAlchemyRoleAssignmentRepository(session).list_assignments()


@router.put("/roles/{user_id}")
async def replace_roles(
    user_id: UUID,
    body: RoleAssignmentBody,
    session: SessionDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    if not body.roles:
        raise HTTPException(
            status_code=422,
            detail="At least one application role is required.",
        )
    repository = SqlAlchemyRoleAssignmentRepository(session)
    return await repository.replace_roles(user_id, frozenset(body.roles))
