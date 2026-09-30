from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.domain.purchase_requests import Money


@dataclass(frozen=True, slots=True)
class BudgetConstraint:
    owner_type: str
    owner_id: UUID
    available: Money


class BudgetConstraintReader(Protocol):
    async def get_applicable_constraints(
        self,
        requester_user_id: UUID,
        currency: str,
    ) -> tuple[BudgetConstraint, ...]: ...
