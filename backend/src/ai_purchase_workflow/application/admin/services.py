from dataclasses import dataclass

from ai_purchase_workflow.application.admin.budgets import ManageBudgets
from ai_purchase_workflow.application.admin.departments import ManageDepartments
from ai_purchase_workflow.application.admin.offers import ManageOffers
from ai_purchase_workflow.application.admin.products import ManageProducts
from ai_purchase_workflow.application.admin.roles import ManageRoleAssignments
from ai_purchase_workflow.application.admin.vendors import ManageVendors


@dataclass(frozen=True, slots=True)
class AdminServices:
    departments: ManageDepartments
    products: ManageProducts
    vendors: ManageVendors
    offers: ManageOffers
    budgets: ManageBudgets
    roles: ManageRoleAssignments
