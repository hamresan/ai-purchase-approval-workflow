from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.access.role_reader import RoleReader
from ai_purchase_workflow.application.access.roles import ApplicationRole
from ai_purchase_workflow.infrastructure.access.models import ApplicationUserRoleModel


class SqlAlchemyRoleReader(RoleReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_roles(self, user_id: UUID) -> frozenset[ApplicationRole]:
        result = await self._session.execute(
            select(ApplicationUserRoleModel.role).where(
                ApplicationUserRoleModel.user_id == user_id
            )
        )
        return frozenset(ApplicationRole(value) for value in result.scalars())
