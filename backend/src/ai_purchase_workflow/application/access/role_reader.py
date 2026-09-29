from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.application.access.roles import ApplicationRole


class RoleReader(Protocol):
    async def get_roles(self, user_id: UUID) -> frozenset[ApplicationRole]: ...
