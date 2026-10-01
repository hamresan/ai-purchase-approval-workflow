from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.admin import BudgetRecord, BudgetRepository, BudgetValues
from ai_purchase_workflow.infrastructure.trusted_data.models import BudgetLimitModel


def _record(row: BudgetLimitModel) -> BudgetRecord:
    return BudgetRecord(row.id, cast(Literal["USER", "DEPARTMENT"], row.owner_type), row.user_id, row.department_id, row.amount, row.currency, row.is_active)


def _apply(row: BudgetLimitModel, values: BudgetValues) -> None:
    row.owner_type = values.owner_type
    row.user_id = values.user_id
    row.department_id = values.department_id
    row.amount = values.amount
    row.currency = values.currency
    row.is_active = values.is_active


class SqlAlchemyBudgetRepository(BudgetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_budgets(self) -> tuple[BudgetRecord, ...]:
        result = await self._session.execute(select(BudgetLimitModel))
        return tuple(_record(row) for row in result.scalars())

    async def create_budget(self, values: BudgetValues) -> BudgetRecord:
        row = BudgetLimitModel(id=uuid4(), owner_type=values.owner_type, user_id=values.user_id, department_id=values.department_id, amount=values.amount, currency=values.currency, is_active=values.is_active)
        self._session.add(row)
        await self._session.commit()
        return _record(row)

    async def update_budget(self, budget_id: UUID, values: BudgetValues) -> BudgetRecord | None:
        row = await self._session.get(BudgetLimitModel, budget_id)
        if row is None:
            return None
        _apply(row, values)
        await self._session.commit()
        return _record(row)
