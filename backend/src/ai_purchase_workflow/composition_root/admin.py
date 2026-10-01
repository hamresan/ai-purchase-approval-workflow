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
from ai_purchase_workflow.infrastructure.access.sqlalchemy_role_assignment_repository import (
    SqlAlchemyRoleAssignmentRepository,
)
from ai_purchase_workflow.infrastructure.trusted_data.budget_repository import (
    SqlAlchemyBudgetRepository,
)
from ai_purchase_workflow.infrastructure.trusted_data.department_repository import (
    SqlAlchemyDepartmentRepository,
)
from ai_purchase_workflow.infrastructure.trusted_data.offer_repository import (
    SqlAlchemyOfferRepository,
)
from ai_purchase_workflow.infrastructure.trusted_data.product_repository import (
    SqlAlchemyProductRepository,
)
from ai_purchase_workflow.infrastructure.trusted_data.vendor_repository import (
    SqlAlchemyVendorRepository,
)


def build_admin_services(session: AsyncSession) -> AdminServices:
    return AdminServices(
        departments=ManageDepartments(SqlAlchemyDepartmentRepository(session)),
        products=ManageProducts(SqlAlchemyProductRepository(session)),
        vendors=ManageVendors(SqlAlchemyVendorRepository(session)),
        offers=ManageOffers(SqlAlchemyOfferRepository(session)),
        budgets=ManageBudgets(SqlAlchemyBudgetRepository(session)),
        roles=ManageRoleAssignments(SqlAlchemyRoleAssignmentRepository(session)),
    )
