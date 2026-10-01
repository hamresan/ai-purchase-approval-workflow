from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import (
    ManageBudgets,
    ManageDepartments,
    ManageOffers,
    ManageProducts,
    ManageVendors,
)
from ai_purchase_workflow.infrastructure.trusted_data.budget_repository import SqlAlchemyBudgetRepository
from ai_purchase_workflow.infrastructure.trusted_data.department_repository import SqlAlchemyDepartmentRepository
from ai_purchase_workflow.infrastructure.trusted_data.offer_repository import SqlAlchemyOfferRepository
from ai_purchase_workflow.infrastructure.trusted_data.product_repository import SqlAlchemyProductRepository
from ai_purchase_workflow.infrastructure.trusted_data.vendor_repository import SqlAlchemyVendorRepository
from ai_purchase_workflow.presentation.dependencies import get_session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]


def get_manage_departments(session: SessionDependency) -> ManageDepartments:
    return ManageDepartments(SqlAlchemyDepartmentRepository(session))


def get_manage_products(session: SessionDependency) -> ManageProducts:
    return ManageProducts(SqlAlchemyProductRepository(session))


def get_manage_vendors(session: SessionDependency) -> ManageVendors:
    return ManageVendors(SqlAlchemyVendorRepository(session))


def get_manage_offers(session: SessionDependency) -> ManageOffers:
    return ManageOffers(SqlAlchemyOfferRepository(session))


def get_manage_budgets(session: SessionDependency) -> ManageBudgets:
    return ManageBudgets(SqlAlchemyBudgetRepository(session))
