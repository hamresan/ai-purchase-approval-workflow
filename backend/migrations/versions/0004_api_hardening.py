"""Add purchase request idempotency keys."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_api_hardening"
down_revision: str | None = "0003_human_approval_resume"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "purchase_request_idempotency",
        sa.Column("key", sa.String(length=200), primary_key=True),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requests.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("purchase_request_idempotency")
