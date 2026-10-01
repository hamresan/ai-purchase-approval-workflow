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


class ManageRoleAssignments:
    def __init__(self, repository: RoleAssignmentRepository) -> None:
        self._repository = repository

    async def list_assignments(self) -> tuple[RoleAssignment, ...]:
        return await self._repository.list_assignments()

    async def replace_roles(
        self, user_id: UUID, roles: frozenset[ApplicationRole]
    ) -> RoleAssignment:
        return await self._repository.replace_roles(user_id, roles)
