from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_trusted_data_schema_enforces_budget_owner_shape(db_session: AsyncSession) -> None:
    result = await db_session.execute(
        text(
            """
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'budget_limits'
              AND constraint_type = 'CHECK'
            """
        )
    )

    names = {row[0] for row in result}

    assert "ck_budget_limits_owner" in names
    assert "ck_budget_limits_nonnegative_amount" in names


async def test_trusted_data_schema_has_owner_specific_budget_uniqueness(
    db_session: AsyncSession,
) -> None:
    result = await db_session.execute(
        text(
            """
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'budget_limits'
            """
        )
    )

    names = {row[0] for row in result}

    assert "uq_budget_limits_user_currency" in names
    assert "uq_budget_limits_department_currency" in names
