from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.trusted_data import BudgetConstraint, BudgetConstraintReader
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, Money
from ai_purchase_workflow.infrastructure.trusted_data.models import (
    BudgetLimitModel,
    DepartmentMembershipModel,
    DepartmentModel,
)


class SqlAlchemyBudgetConstraintReader(BudgetConstraintReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_applicable_constraints(
        self,
        requester_user_id,
        currency: str,
    ) -> tuple[BudgetConstraint, ...]:
        department_ids = select(DepartmentMembershipModel.department_id).join(
            DepartmentModel,
            DepartmentModel.id == DepartmentMembershipModel.department_id,
        ).where(
            DepartmentMembershipModel.user_id == requester_user_id,
            DepartmentMembershipModel.is_active.is_(True),
            DepartmentModel.is_active.is_(True),
        )
        rows = (
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
        ).scalars().all()
        if not rows:
            raise DomainValidationError(
                "No trusted budget data is available for this requester."
            )
        return tuple(
            BudgetConstraint(
                owner_type=row.owner_type,
                owner_id=row.user_id if row.user_id is not None else row.department_id,
                available=Money(row.amount, row.currency),
            )
            for row in rows
            if row.user_id is not None or row.department_id is not None
        )
