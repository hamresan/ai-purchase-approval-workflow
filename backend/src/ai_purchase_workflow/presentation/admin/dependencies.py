from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import (
    AdminServices,
    ManageBudgets,
    ManageDepartments,
    ManageOffers,
    ManageProducts,
    ManageRoleAssignments,
    ManageVendors,
)
from ai_purchase_workflow.presentation.dependencies import get_session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def get_admin_services(request: Request, session: SessionDependency) -> AdminServices:
    return request.app.state.admin_services_builder(session)


AdminServicesDependency = Annotated[AdminServices, Depends(get_admin_services)]


def get_manage_departments(services: AdminServicesDependency) -> ManageDepartments:
    return services.departments


def get_manage_products(services: AdminServicesDependency) -> ManageProducts:
    return services.products


def get_manage_vendors(services: AdminServicesDependency) -> ManageVendors:
    return services.vendors


def get_manage_offers(services: AdminServicesDependency) -> ManageOffers:
    return services.offers


def get_manage_budgets(services: AdminServicesDependency) -> ManageBudgets:
    return services.budgets


def get_manage_role_assignments(services: AdminServicesDependency) -> ManageRoleAssignments:
    return services.roles
