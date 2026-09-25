"""Initial migration baseline."""

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: tuple[str, ...] | None = None
depends_on: tuple[str, ...] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
