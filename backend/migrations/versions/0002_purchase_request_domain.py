"""Add purchase request domain persistence."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_purchase_request_domain"
down_revision: str | None = "0001_baseline"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "purchase_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("requester_name", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("items", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_purchase_requests_status", "purchase_requests", ["status"])
    op.create_index("ix_purchase_requests_created_at", "purchase_requests", ["created_at"])
    op.create_table(
        "draft_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requests.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("items", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "approval_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requests.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("decided_by", sa.String(length=200), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "audit_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchase_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("request_id", "sequence", name="uq_audit_entries_request_sequence"),
    )
    op.create_index("ix_audit_entries_request_id", "audit_entries", ["request_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_entries_request_id", table_name="audit_entries")
    op.drop_table("audit_entries")
    op.drop_table("approval_decisions")
    op.drop_table("draft_orders")
    op.drop_index("ix_purchase_requests_created_at", table_name="purchase_requests")
    op.drop_index("ix_purchase_requests_status", table_name="purchase_requests")
    op.drop_table("purchase_requests")
