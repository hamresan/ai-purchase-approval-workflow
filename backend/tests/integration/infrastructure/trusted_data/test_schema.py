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


async def test_organization_member_schema_links_identity_once_and_owns_memberships(
    db_session: AsyncSession,
) -> None:
    indexes = await db_session.execute(
        text(
            """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'organization_members'
            """
        )
    )
    foreign_keys = await db_session.execute(
        text(
            """
            SELECT kcu.column_name, ccu.table_name, ccu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.constraint_schema = kcu.constraint_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.constraint_schema = tc.constraint_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_name = 'department_memberships'
            """
        )
    )

    member_indexes = {row[0]: row[1] for row in indexes}
    membership_foreign_keys = {(row[0], row[1], row[2]) for row in foreign_keys}

    assert any(
        "identity_user_id" in definition and "UNIQUE" in definition
        for definition in member_indexes.values()
    )
    assert ("member_id", "organization_members", "id") in membership_foreign_keys
