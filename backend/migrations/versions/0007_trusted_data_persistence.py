"""Add organization, trusted catalog, vendor, and budget persistence."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_trusted_data"
down_revision: str | None = "0006_requester_identity"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "department_memberships",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["identity_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(
        "ix_department_memberships_department_id",
        "department_memberships",
        ["department_id"],
    )
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "trusted_offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unit_price_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("available_quantity", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "product_id",
            "vendor_id",
            name="uq_trusted_offers_product_vendor",
        ),
    )
    op.create_index("ix_trusted_offers_product_id", "trusted_offers", ["product_id"])
    op.create_index("ix_trusted_offers_vendor_id", "trusted_offers", ["vendor_id"])
    op.create_table(
        "budget_limits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_type", sa.String(length=20), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "(owner_type = 'USER' AND user_id IS NOT NULL AND department_id IS NULL) "
            "OR (owner_type = 'DEPARTMENT' AND user_id IS NULL AND department_id IS NOT NULL)",
            name="ck_budget_limits_owner",
        ),
        sa.CheckConstraint("amount >= 0", name="ck_budget_limits_nonnegative_amount"),
        sa.ForeignKeyConstraint(["user_id"], ["identity_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_budget_limits_owner_type", "budget_limits", ["owner_type"])
    op.create_index("ix_budget_limits_user_id", "budget_limits", ["user_id"])
    op.create_index("ix_budget_limits_department_id", "budget_limits", ["department_id"])
    op.create_index(
        "uq_budget_limits_user_currency",
        "budget_limits",
        ["user_id", "currency"],
        unique=True,
        postgresql_where=sa.text("owner_type = 'USER'"),
    )
    op.create_index(
        "uq_budget_limits_department_currency",
        "budget_limits",
        ["department_id", "currency"],
        unique=True,
        postgresql_where=sa.text("owner_type = 'DEPARTMENT'"),
    )


def downgrade() -> None:
    op.drop_table("budget_limits")
    op.drop_table("trusted_offers")
    op.drop_table("vendors")
    op.drop_table("products")
    op.drop_table("department_memberships")
    op.drop_table("departments")
