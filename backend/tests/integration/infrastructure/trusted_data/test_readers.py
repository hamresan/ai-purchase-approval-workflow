from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.domain.purchase_requests import DomainValidationError
from ai_purchase_workflow.infrastructure.trusted_data.budget_reader import (
    SqlAlchemyBudgetConstraintReader,
)
from ai_purchase_workflow.infrastructure.trusted_data.catalog_reader import (
    SqlAlchemyTrustedCatalogReader,
)
from ai_purchase_workflow.infrastructure.trusted_data.models import (
    BudgetLimitModel,
    DepartmentMembershipModel,
    DepartmentModel,
    ProductModel,
    TrustedOfferModel,
    VendorModel,
)

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
DEPARTMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


async def test_catalog_reader_returns_active_trusted_offer(db_session: AsyncSession) -> None:
    product = ProductModel(id=UUID("10000000-0000-0000-0000-000000000001"), name="Laptop stand", is_active=True)
    vendor = VendorModel(id=UUID("20000000-0000-0000-0000-000000000001"), name="Acme", is_active=True)
    db_session.add_all([
        product,
        vendor,
        TrustedOfferModel(
            id=UUID("30000000-0000-0000-0000-000000000001"),
            product_id=product.id,
            vendor_id=vendor.id,
            unit_price_amount=Decimal("35.00"),
            currency="USD",
            available_quantity=10,
            is_active=True,
        ),
    ])
    await db_session.commit()

    item = await SqlAlchemyTrustedCatalogReader(db_session).find_item("laptop stands")

    assert item.description == "Laptop stand"
    assert item.vendor_name == "Acme"
    assert item.unit_price.amount == Decimal("35.00")
    assert item.available_quantity == 10


async def test_catalog_reader_rejects_missing_or_inactive_data(db_session: AsyncSession) -> None:
    with pytest.raises(DomainValidationError, match="No trusted vendor data"):
        await SqlAlchemyTrustedCatalogReader(db_session).find_item("Unknown")


async def test_budget_reader_returns_user_and_department_constraints(
    db_session: AsyncSession,
) -> None:
    department = DepartmentModel(id=DEPARTMENT_ID, name="Engineering", is_active=True)
    db_session.add(department)
    await db_session.flush()
    db_session.add(
        DepartmentMembershipModel(
            user_id=USER_ID,
            department_id=DEPARTMENT_ID,
            is_active=True,
        )
    )
    db_session.add_all([
        BudgetLimitModel(
            id=UUID("40000000-0000-0000-0000-000000000001"),
            owner_type="USER",
            user_id=USER_ID,
            department_id=None,
            amount=Decimal("500.00"),
            currency="USD",
            is_active=True,
        ),
        BudgetLimitModel(
            id=UUID("40000000-0000-0000-0000-000000000002"),
            owner_type="DEPARTMENT",
            user_id=None,
            department_id=DEPARTMENT_ID,
            amount=Decimal("1000.00"),
            currency="USD",
            is_active=True,
        ),
    ])
    await db_session.commit()

    constraints = await SqlAlchemyBudgetConstraintReader(db_session).get_applicable_constraints(
        USER_ID,
        "USD",
    )

    assert {(item.owner_type, item.available.amount) for item in constraints} == {
        ("USER", Decimal("500.00")),
        ("DEPARTMENT", Decimal("1000.00")),
    }


async def test_budget_reader_rejects_requester_without_applicable_budget(
    db_session: AsyncSession,
) -> None:
    with pytest.raises(DomainValidationError, match="No trusted budget data"):
        await SqlAlchemyBudgetConstraintReader(db_session).get_applicable_constraints(
            USER_ID,
            "USD",
        )
