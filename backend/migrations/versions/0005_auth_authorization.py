"""Add Identity schema and application authorization roles."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_auth_authorization"
down_revision: str | None = "0004_api_hardening"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

user_status = sa.Enum(
    "PENDING", "ACTIVE", "SUSPENDED", "DISABLED",
    name="identity_user_status", native_enum=False,
)
identity_type = sa.Enum("MOBILE", "EMAIL", name="identity_type", native_enum=False)
otp_identifier_type = sa.Enum(
    "MOBILE", "EMAIL", name="identity_otp_identifier_type", native_enum=False,
)
otp_purpose = sa.Enum(
    "REGISTRATION",
    "LOGIN",
    "VERIFY_EMAIL",
    "CHANGE_EMAIL",
    "CHANGE_MOBILE",
    "ACCOUNT_RECOVERY",
    name="identity_otp_purpose",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "identity_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("status", user_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_identity_users_status", "identity_users", ["status"])
    op.create_index("ix_identity_users_created_at", "identity_users", ["created_at"])

    op.create_table(
        "identity_user_identities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", identity_type, nullable=False),
        sa.Column("value", sa.String(length=320), nullable=False),
        sa.Column("normalized_value", sa.String(length=320), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["identity_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "type",
            "normalized_value",
            name="uq_identity_user_identities_type_normalized_value",
        ),
    )
    op.create_index(
        "ix_identity_user_identities_user_id",
        "identity_user_identities",
        ["user_id"],
    )
    op.create_index(
        "ix_identity_user_identities_normalized_value",
        "identity_user_identities",
        ["normalized_value"],
    )

    op.create_table(
        "identity_external_identities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.String(length=320), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["identity_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider",
            "subject",
            name="uq_identity_external_identities_provider_subject",
        ),
    )
    op.create_index(
        "ix_identity_external_identities_user_id",
        "identity_external_identities",
        ["user_id"],
    )

    op.create_table(
        "identity_otp_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("identity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("identifier_type", otp_identifier_type, nullable=False),
        sa.Column("normalized_destination", sa.String(length=320), nullable=False),
        sa.Column("destination_snapshot", sa.String(length=320), nullable=False),
        sa.Column("purpose", otp_purpose, nullable=False),
        sa.Column("code_hash", sa.String(length=512), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resend_available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts_count", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["identity_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["identity_id"],
            ["identity_user_identities.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "user_id",
        "identity_id",
        "normalized_destination",
        "purpose",
        "expires_at",
        "consumed_at",
        "created_at",
    ):
        op.create_index(
            f"ix_identity_otp_challenges_{column}",
            "identity_otp_challenges",
            [column],
        )
    op.create_index(
        "ix_identity_otp_challenges_destination_purpose_created_at",
        "identity_otp_challenges",
        ["normalized_destination", "purpose", "created_at"],
    )

    op.create_table(
        "identity_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=512), nullable=False),
        sa.Column("family_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("replaced_by_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("family_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("device_info", sa.String(length=512), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["identity_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["parent_session_id"],
            ["identity_sessions.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["replaced_by_session_id"],
            ["identity_sessions.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refresh_token_hash"),
    )
    for column in (
        "user_id",
        "family_id",
        "expires_at",
        "family_expires_at",
        "revoked_at",
        "created_at",
    ):
        op.create_index(f"ix_identity_sessions_{column}", "identity_sessions", [column])

    op.create_table(
        "application_user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["identity_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role"),
    )


def downgrade() -> None:
    op.drop_table("application_user_roles")
    op.drop_table("identity_sessions")
    op.drop_table("identity_otp_challenges")
    op.drop_table("identity_external_identities")
    op.drop_table("identity_user_identities")
    op.drop_table("identity_users")
