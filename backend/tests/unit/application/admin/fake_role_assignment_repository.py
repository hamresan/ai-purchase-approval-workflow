from uuid import UUID

from ai_purchase_workflow.application.access import ApplicationRole
from ai_purchase_workflow.application.admin import RoleAssignment, RoleAssignmentRepository


class FakeRoleAssignmentRepository(RoleAssignmentRepository):
    def __init__(self) -> None:
        self._assignments: dict[UUID, frozenset[ApplicationRole]] = {}

    async def list_assignments(self) -> tuple[RoleAssignment, ...]:
        return tuple(
            RoleAssignment(user_id, roles)
            for user_id, roles in sorted(self._assignments.items(), key=lambda item: str(item[0]))
        )

    async def replace_roles(
        self, user_id: UUID, roles: frozenset[ApplicationRole]
    ) -> RoleAssignment:
        self._assignments[user_id] = roles
        return RoleAssignment(user_id, roles)
