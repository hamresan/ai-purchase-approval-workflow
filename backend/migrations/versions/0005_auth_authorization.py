"""Add Identity schema and application authorization roles."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from identity.migrations import identity_metadata
from sqlalchemy.dialects import postgresql

revision: str = "0005_auth_authorization"
down_revision: str | None = "0004_api_hardening"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    identity_metadata().create_all(bind=connection, checkfirst=True)
    op.create_table(
        "application_user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["identity_users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "role"),
    )


def downgrade() -> None:
    op.drop_table("application_user_roles")
    connection = op.get_bind()
    identity_metadata().drop_all(bind=connection, checkfirst=True)
