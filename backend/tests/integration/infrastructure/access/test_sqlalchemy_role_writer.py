from uuid import UUID

from identity.infrastructure.persistence.sqlalchemy.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import UTC, datetime
from identity.domain import UserStatus

from ai_purchase_workflow.application.access import ApplicationRole
from ai_purchase_workflow.infrastructure.access import SqlAlchemyRoleReader, SqlAlchemyRoleWriter


async def test_role_writer_is_idempotent(db_session: AsyncSession) -> None:
    user_id = UUID("11111111-1111-1111-1111-111111111111")
    now = datetime.now(UTC)
    db_session.add(
        UserModel(
            id=user_id,
            full_name="Bootstrap Admin",
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
    )
    await db_session.commit()
    writer = SqlAlchemyRoleWriter(db_session)

    await writer.ensure_role(user_id, ApplicationRole.ADMIN)
    await writer.ensure_role(user_id, ApplicationRole.ADMIN)

    roles = await SqlAlchemyRoleReader(db_session).get_roles(user_id)
    assert roles == frozenset({ApplicationRole.ADMIN})
