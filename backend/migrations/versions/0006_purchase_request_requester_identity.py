"""Persist the authenticated requester identity on purchase requests."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_requester_identity"
down_revision: str | None = "0005_auth_authorization"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "purchase_requests",
        sa.Column("requester_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_purchase_requests_requester_user_id",
        "purchase_requests",
        "identity_users",
        ["requester_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_purchase_requests_requester_user_id",
        "purchase_requests",
        ["requester_user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_purchase_requests_requester_user_id", table_name="purchase_requests")
    op.drop_constraint(
        "fk_purchase_requests_requester_user_id",
        "purchase_requests",
        type_="foreignkey",
    )
    op.drop_column("purchase_requests", "requester_user_id")
