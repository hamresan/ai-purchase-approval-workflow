from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.access import ApplicationRole, RoleWriter
from ai_purchase_workflow.infrastructure.access.models import ApplicationUserRoleModel


class SqlAlchemyRoleWriter(RoleWriter):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ensure_role(self, user_id: UUID, role: ApplicationRole) -> None:
        statement = (
            insert(ApplicationUserRoleModel)
            .values(user_id=user_id, role=role.value)
            .on_conflict_do_nothing(
                index_elements=[ApplicationUserRoleModel.user_id, ApplicationUserRoleModel.role]
            )
        )
        await self._session.execute(statement)
        await self._session.commit()
