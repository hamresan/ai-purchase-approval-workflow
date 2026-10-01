from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from ai_purchase_workflow.application.access import ApplicationPrincipal, AuthorizationPolicy
from ai_purchase_workflow.application.admin import (
    BudgetValues,
    ManageBudgets,
    ManageOffers,
    ManageProducts,
    ManageRoleAssignments,
    ManageVendors,
    OfferValues,
)
from ai_purchase_workflow.presentation.admin.dependencies import (
    get_manage_budgets,
    get_manage_offers,
    get_manage_products,
    get_manage_role_assignments,
    get_manage_vendors,
)
from ai_purchase_workflow.presentation.admin.resource_schemas import (
    BudgetBody,
    BudgetResponse,
    NamedResourceCreateBody,
    NamedResourceUpdateBody,
    OfferBody,
    OfferResponse,
    ProductResponse,
    RoleAssignmentBody,
    RoleAssignmentResponse,
    VendorResponse,
)
from ai_purchase_workflow.presentation.auth import CurrentPrincipalDependency

router = APIRouter(prefix="/api/admin", tags=["admin-resources"])
ProductsDependency = Annotated[ManageProducts, Depends(get_manage_products)]
VendorsDependency = Annotated[ManageVendors, Depends(get_manage_vendors)]
OffersDependency = Annotated[ManageOffers, Depends(get_manage_offers)]
BudgetsDependency = Annotated[ManageBudgets, Depends(get_manage_budgets)]
RolesDependency = Annotated[ManageRoleAssignments, Depends(get_manage_role_assignments)]


def _authorize(principal: ApplicationPrincipal) -> None:
    AuthorizationPolicy().require_admin(principal)


def _offer_values(body: OfferBody) -> OfferValues:
    return OfferValues(
        body.product_id,
        body.vendor_id,
        body.unit_price_amount,
        body.currency,
        body.available_quantity,
        body.is_active,
    )


def _budget_values(body: BudgetBody) -> BudgetValues:
    return BudgetValues(
        body.owner_type,
        body.user_id,
        body.department_id,
        body.amount,
        body.currency,
        body.is_active,
    )


@router.get("/products", response_model=list[ProductResponse])
async def list_products(manager: ProductsDependency, principal: CurrentPrincipalDependency):
    _authorize(principal)
    return [ProductResponse.from_record(record) for record in await manager.list_products()]


@router.post("/products", status_code=201, response_model=ProductResponse)
async def create_product(
    body: NamedResourceCreateBody,
    manager: ProductsDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    try:
        return ProductResponse.from_record(await manager.create_product(body.name.strip()))
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="Product name already exists.") from error


@router.put("/products/{resource_id}", response_model=ProductResponse)
async def update_product(
    resource_id: UUID,
    body: NamedResourceUpdateBody,
    manager: ProductsDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    try:
        record = await manager.update_product(resource_id, body.name.strip(), body.is_active)
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="Product name already exists.") from error
    if record is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return ProductResponse.from_record(record)


@router.get("/vendors", response_model=list[VendorResponse])
async def list_vendors(manager: VendorsDependency, principal: CurrentPrincipalDependency):
    _authorize(principal)
    return [VendorResponse.from_record(record) for record in await manager.list_vendors()]


@router.post("/vendors", status_code=201, response_model=VendorResponse)
async def create_vendor(
    body: NamedResourceCreateBody,
    manager: VendorsDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    try:
        return VendorResponse.from_record(await manager.create_vendor(body.name.strip()))
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="Vendor name already exists.") from error


@router.put("/vendors/{resource_id}", response_model=VendorResponse)
async def update_vendor(
    resource_id: UUID,
    body: NamedResourceUpdateBody,
    manager: VendorsDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    try:
        record = await manager.update_vendor(resource_id, body.name.strip(), body.is_active)
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="Vendor name already exists.") from error
    if record is None:
        raise HTTPException(status_code=404, detail="Vendor not found.")
    return VendorResponse.from_record(record)


@router.get("/offers", response_model=list[OfferResponse])
async def list_offers(manager: OffersDependency, principal: CurrentPrincipalDependency):
    _authorize(principal)
    return [OfferResponse.from_record(record) for record in await manager.list_offers()]


@router.post("/offers", status_code=201, response_model=OfferResponse)
async def create_offer(
    body: OfferBody,
    manager: OffersDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    try:
        return OfferResponse.from_record(await manager.create_offer(_offer_values(body)))
    except IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="Trusted offer conflicts with existing trusted data.",
        ) from error


@router.put("/offers/{resource_id}", response_model=OfferResponse)
async def update_offer(
    resource_id: UUID,
    body: OfferBody,
    manager: OffersDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    try:
        record = await manager.update_offer(resource_id, _offer_values(body))
    except IntegrityError as error:
        raise HTTPException(
            status_code=409, detail="Trusted offer conflicts with existing trusted data."
        ) from error
    if record is None:
        raise HTTPException(status_code=404, detail="Trusted offer not found.")
    return OfferResponse.from_record(record)


@router.get("/budgets", response_model=list[BudgetResponse])
async def list_budgets(manager: BudgetsDependency, principal: CurrentPrincipalDependency):
    _authorize(principal)
    return [BudgetResponse.from_record(record) for record in await manager.list_budgets()]


@router.post("/budgets", status_code=201, response_model=BudgetResponse)
async def create_budget(
    body: BudgetBody,
    manager: BudgetsDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    try:
        return BudgetResponse.from_record(await manager.create_budget(_budget_values(body)))
    except IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="Budget conflicts with existing trusted data.",
        ) from error


@router.put("/budgets/{resource_id}", response_model=BudgetResponse)
async def update_budget(
    resource_id: UUID,
    body: BudgetBody,
    manager: BudgetsDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    try:
        record = await manager.update_budget(resource_id, _budget_values(body))
    except IntegrityError as error:
        raise HTTPException(
            status_code=409, detail="Budget conflicts with existing trusted data."
        ) from error
    if record is None:
        raise HTTPException(status_code=404, detail="Budget not found.")
    return BudgetResponse.from_record(record)


@router.get("/roles", response_model=list[RoleAssignmentResponse])
async def list_roles(manager: RolesDependency, principal: CurrentPrincipalDependency):
    _authorize(principal)
    return [
        RoleAssignmentResponse.from_record(record) for record in await manager.list_assignments()
    ]


@router.put("/roles/{user_id}", response_model=RoleAssignmentResponse)
async def replace_roles(
    user_id: UUID,
    body: RoleAssignmentBody,
    manager: RolesDependency,
    principal: CurrentPrincipalDependency,
):
    _authorize(principal)
    if not body.roles:
        raise HTTPException(status_code=422, detail="At least one application role is required.")
    record = await manager.replace_roles(user_id, frozenset(body.roles))
    return RoleAssignmentResponse.from_record(record)
