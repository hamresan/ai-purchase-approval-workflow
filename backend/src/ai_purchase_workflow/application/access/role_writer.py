from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.application.access.roles import ApplicationRole


class RoleWriter(Protocol):
    async def ensure_role(self, user_id: UUID, role: ApplicationRole) -> None: ...
