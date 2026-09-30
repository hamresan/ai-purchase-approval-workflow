from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.access import ApplicationRole
from ai_purchase_workflow.application.admin import RoleAssignment, RoleAssignmentRepository
from ai_purchase_workflow.infrastructure.access.models import ApplicationUserRoleModel


class SqlAlchemyRoleAssignmentRepository(RoleAssignmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_assignments(self) -> tuple[RoleAssignment, ...]:
        rows = (await self._session.execute(
            select(ApplicationUserRoleModel).order_by(ApplicationUserRoleModel.user_id)
        )).scalars().all()
        grouped: dict[object, set[ApplicationRole]] = {}
        for row in rows:
            grouped.setdefault(row.user_id, set()).add(ApplicationRole(row.role))
        return tuple(
            RoleAssignment(user_id, frozenset(roles))
            for user_id, roles in grouped.items()
        )

    async def replace_roles(
        self, user_id, roles: frozenset[ApplicationRole]
    ) -> RoleAssignment:
        await self._session.execute(
            delete(ApplicationUserRoleModel).where(ApplicationUserRoleModel.user_id == user_id)
        )
        self._session.add_all(
            ApplicationUserRoleModel(user_id=user_id, role=role.value)
            for role in sorted(roles, key=lambda value: value.value)
        )
        await self._session.commit()
        return RoleAssignment(user_id, roles)
