from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.trusted_data import BudgetConstraint, BudgetConstraintReader
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, Money
from ai_purchase_workflow.infrastructure.trusted_data.models import (
    BudgetLimitModel,
    DepartmentMembershipModel,
    DepartmentModel,
    OrganizationMemberModel,
)


class SqlAlchemyBudgetConstraintReader(BudgetConstraintReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_applicable_constraints(
        self,
        requester_user_id: UUID,
        currency: str,
    ) -> tuple[BudgetConstraint, ...]:
        department_ids = (
            select(DepartmentMembershipModel.department_id)
            .join(
                OrganizationMemberModel,
                OrganizationMemberModel.id == DepartmentMembershipModel.member_id,
            )
            .join(
                DepartmentModel,
                DepartmentModel.id == DepartmentMembershipModel.department_id,
            )
            .where(
                OrganizationMemberModel.identity_user_id == requester_user_id,
                OrganizationMemberModel.is_active.is_(True),
                DepartmentMembershipModel.is_active.is_(True),
                DepartmentModel.is_active.is_(True),
            )
        )
        rows = (
            (
                await self._session.execute(
                    select(BudgetLimitModel).where(
                        BudgetLimitModel.is_active.is_(True),
                        BudgetLimitModel.currency == currency,
                        or_(
                            BudgetLimitModel.user_id == requester_user_id,
                            BudgetLimitModel.department_id.in_(department_ids),
                        ),
                    )
                )
            )
            .scalars()
            .all()
        )
        if not rows:
            raise DomainValidationError("No trusted budget data is available for this requester.")
        constraints: list[BudgetConstraint] = []
        for row in rows:
            owner_id = row.user_id or row.department_id
            if owner_id is None:
                raise DomainValidationError("Trusted budget data has no valid owner.")
            constraints.append(
                BudgetConstraint(
                    owner_type=row.owner_type,
                    owner_id=owner_id,
                    available=Money(row.amount, row.currency),
                )
            )
        return tuple(constraints)
