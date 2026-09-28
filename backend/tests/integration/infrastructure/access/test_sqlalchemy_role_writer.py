from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.access import ApplicationRole
from ai_purchase_workflow.infrastructure.access import SqlAlchemyRoleReader, SqlAlchemyRoleWriter


async def test_role_writer_is_idempotent(db_session: AsyncSession) -> None:
    user_id = UUID("11111111-1111-1111-1111-111111111111")
    writer = SqlAlchemyRoleWriter(db_session)

    await writer.ensure_role(user_id, ApplicationRole.ADMIN)
    await writer.ensure_role(user_id, ApplicationRole.ADMIN)

    roles = await SqlAlchemyRoleReader(db_session).get_roles(user_id)
    assert roles == frozenset({ApplicationRole.ADMIN})
