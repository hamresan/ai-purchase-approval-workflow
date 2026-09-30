from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.application.access import ApplicationRole


@dataclass(frozen=True, slots=True)
class RoleAssignment:
    user_id: UUID
    roles: frozenset[ApplicationRole]


class RoleAssignmentRepository(Protocol):
    async def list_assignments(self) -> tuple[RoleAssignment, ...]: ...
    async def replace_roles(
        self, user_id: UUID, roles: frozenset[ApplicationRole]
    ) -> RoleAssignment: ...
