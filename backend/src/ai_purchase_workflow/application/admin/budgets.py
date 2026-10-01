from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class BudgetRecord:
    id: UUID
    owner_type: Literal["USER", "DEPARTMENT"]
    user_id: UUID | None
    department_id: UUID | None
    amount: Decimal
    currency: str
    is_active: bool


@dataclass(frozen=True, slots=True)
class BudgetValues:
    owner_type: Literal["USER", "DEPARTMENT"]
    user_id: UUID | None
    department_id: UUID | None
    amount: Decimal
    currency: str
    is_active: bool


class BudgetRepository(Protocol):
    async def list_budgets(self) -> tuple[BudgetRecord, ...]: ...
    async def create_budget(self, values: BudgetValues) -> BudgetRecord: ...
    async def update_budget(
        self, budget_id: UUID, values: BudgetValues
    ) -> BudgetRecord | None: ...


class ManageBudgets:
    def __init__(self, repository: BudgetRepository) -> None:
        self._repository = repository

    async def list_budgets(self) -> tuple[BudgetRecord, ...]:
        return await self._repository.list_budgets()

    async def create_budget(self, values: BudgetValues) -> BudgetRecord:
        return await self._repository.create_budget(values)

    async def update_budget(
        self, budget_id: UUID, values: BudgetValues
    ) -> BudgetRecord | None:
        return await self._repository.update_budget(budget_id, values)
