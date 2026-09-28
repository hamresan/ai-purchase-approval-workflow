from dataclasses import dataclass
from uuid import UUID

from ai_purchase_workflow.application.access.role_writer import RoleWriter
from ai_purchase_workflow.application.access.roles import ApplicationRole


@dataclass(frozen=True, slots=True)
class BootstrapFirstAdmin:
    role_writer: RoleWriter

    async def execute(self, user_id: UUID) -> None:
        await self.role_writer.ensure_role(user_id, ApplicationRole.ADMIN)
