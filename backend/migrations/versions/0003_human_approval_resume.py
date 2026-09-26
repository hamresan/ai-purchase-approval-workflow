"""Add Stage 4 workflow persistence support."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_human_approval_resume"
down_revision: str | None = "0002_purchase_request_domain"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "approval_decisions_request_id_key",
        "approval_decisions",
        type_="unique",
    )
    op.create_index(
        "ix_approval_decisions_request_id",
        "approval_decisions",
        ["request_id"],
    )
    op.create_table(
        "workflow_threads",
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requests.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("thread_id", sa.String(length=200), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("workflow_threads")
    op.drop_index("ix_approval_decisions_request_id", table_name="approval_decisions")
    op.create_unique_constraint(
        "approval_decisions_request_id_key",
        "approval_decisions",
        ["request_id"],
    )
