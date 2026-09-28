from dataclasses import dataclass
from uuid import UUID

from ai_purchase_workflow.application.access.roles import ApplicationRole


@dataclass(frozen=True, slots=True)
class ApplicationPrincipal:
    user_id: UUID
    session_id: UUID
    display_name: str
    roles: frozenset[ApplicationRole]
