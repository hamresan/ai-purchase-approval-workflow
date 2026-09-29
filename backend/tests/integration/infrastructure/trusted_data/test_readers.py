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
    OrganizationMemberModel,
    ProductModel,
    TrustedOfferModel,
    VendorModel,
)

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
DEPARTMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


async def test_catalog_reader_returns_active_trusted_offer(db_session: AsyncSession) -> None:
    product = ProductModel(
        id=UUID("10000000-0000-0000-0000-000000000001"), name="Laptop stand", is_active=True
    )
    vendor = VendorModel(
        id=UUID("20000000-0000-0000-0000-000000000001"), name="Acme", is_active=True
    )
    db_session.add_all([product, vendor])
    await db_session.flush()
    db_session.add(
        TrustedOfferModel(
            id=UUID("30000000-0000-0000-0000-000000000001"),
            product_id=product.id,
            vendor_id=vendor.id,
            unit_price_amount=Decimal("35.00"),
            currency="USD",
            available_quantity=10,
            is_active=True,
        )
    )
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
    member = OrganizationMemberModel(
        id=UUID("50000000-0000-0000-0000-000000000001"),
        identity_user_id=USER_ID,
        is_active=True,
    )
    department = DepartmentModel(id=DEPARTMENT_ID, name="Engineering", is_active=True)
    db_session.add_all([member, department])
    await db_session.flush()
    db_session.add(
        DepartmentMembershipModel(
            member_id=member.id,
            department_id=DEPARTMENT_ID,
            is_active=True,
        )
    )
    db_session.add_all(
        [
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
        ]
    )
    await db_session.commit()

    constraints = await SqlAlchemyBudgetConstraintReader(db_session).get_applicable_constraints(
        USER_ID,
        "USD",
    )

    assert {(item.owner_type, item.available.amount) for item in constraints} == {
        ("USER", Decimal("500.00")),
        ("DEPARTMENT", Decimal("1000.00")),
    }


async def test_budget_reader_returns_user_constraint_without_department(
    db_session: AsyncSession,
) -> None:
    db_session.add(
        BudgetLimitModel(
            id=UUID("40000000-0000-0000-0000-000000000020"),
            owner_type="USER",
            user_id=USER_ID,
            department_id=None,
            amount=Decimal("500.00"),
            currency="USD",
            is_active=True,
        )
    )
    await db_session.commit()

    constraints = await SqlAlchemyBudgetConstraintReader(db_session).get_applicable_constraints(
        USER_ID,
        "USD",
    )

    assert [(item.owner_type, item.available.amount) for item in constraints] == [
        ("USER", Decimal("500.00"))
    ]


async def test_budget_reader_returns_department_constraint_without_user_budget(
    db_session: AsyncSession,
) -> None:
    member = OrganizationMemberModel(
        id=UUID("50000000-0000-0000-0000-000000000020"),
        identity_user_id=USER_ID,
        is_active=True,
    )
    department = DepartmentModel(id=DEPARTMENT_ID, name="Engineering", is_active=True)
    db_session.add_all([member, department])
    await db_session.flush()
    db_session.add_all(
        [
            DepartmentMembershipModel(
                member_id=member.id,
                department_id=DEPARTMENT_ID,
                is_active=True,
            ),
            BudgetLimitModel(
                id=UUID("40000000-0000-0000-0000-000000000021"),
                owner_type="DEPARTMENT",
                user_id=None,
                department_id=DEPARTMENT_ID,
                amount=Decimal("1000.00"),
                currency="USD",
                is_active=True,
            ),
        ]
    )
    await db_session.commit()

    constraints = await SqlAlchemyBudgetConstraintReader(db_session).get_applicable_constraints(
        USER_ID,
        "USD",
    )

    assert [(item.owner_type, item.available.amount) for item in constraints] == [
        ("DEPARTMENT", Decimal("1000.00"))
    ]


async def test_budget_reader_rejects_requester_without_applicable_budget(
    db_session: AsyncSession,
) -> None:
    with pytest.raises(DomainValidationError, match="No trusted budget data"):
        await SqlAlchemyBudgetConstraintReader(db_session).get_applicable_constraints(
            USER_ID,
            "USD",
        )


@pytest.mark.parametrize(
    ("product_active", "vendor_active", "offer_active"),
    [
        (False, True, True),
        (True, False, True),
        (True, True, False),
    ],
)
async def test_catalog_reader_rejects_inactive_trusted_data(
    db_session: AsyncSession,
    product_active: bool,
    vendor_active: bool,
    offer_active: bool,
) -> None:
    product = ProductModel(
        id=UUID("10000000-0000-0000-0000-000000000010"),
        name="Inactive test product",
        is_active=product_active,
    )
    vendor = VendorModel(
        id=UUID("20000000-0000-0000-0000-000000000010"),
        name="Inactive test vendor",
        is_active=vendor_active,
    )
    db_session.add_all([product, vendor])
    await db_session.flush()
    db_session.add(
        TrustedOfferModel(
            id=UUID("30000000-0000-0000-0000-000000000010"),
            product_id=product.id,
            vendor_id=vendor.id,
            unit_price_amount=Decimal("25.00"),
            currency="USD",
            available_quantity=5,
            is_active=offer_active,
        )
    )
    await db_session.commit()

    with pytest.raises(DomainValidationError, match="No trusted vendor data"):
        await SqlAlchemyTrustedCatalogReader(db_session).find_item("Inactive test product")


@pytest.mark.parametrize(
    ("member_active", "department_active", "membership_active", "budget_active"),
    [
        (False, True, True, True),
        (True, False, True, True),
        (True, True, False, True),
        (True, True, True, False),
    ],
)
async def test_budget_reader_ignores_inactive_department_budget_path(
    db_session: AsyncSession,
    member_active: bool,
    department_active: bool,
    membership_active: bool,
    budget_active: bool,
) -> None:
    member = OrganizationMemberModel(
        id=UUID("50000000-0000-0000-0000-000000000002"),
        identity_user_id=USER_ID,
        is_active=member_active,
    )
    department = DepartmentModel(
        id=DEPARTMENT_ID,
        name="Engineering",
        is_active=department_active,
    )
    db_session.add_all([member, department])
    await db_session.flush()
    db_session.add(
        DepartmentMembershipModel(
            member_id=member.id,
            department_id=DEPARTMENT_ID,
            is_active=membership_active,
        )
    )
    db_session.add(
        BudgetLimitModel(
            id=UUID("40000000-0000-0000-0000-000000000010"),
            owner_type="DEPARTMENT",
            user_id=None,
            department_id=DEPARTMENT_ID,
            amount=Decimal("1000.00"),
            currency="USD",
            is_active=budget_active,
        )
    )
    await db_session.commit()

    with pytest.raises(DomainValidationError, match="No trusted budget data"):
        await SqlAlchemyBudgetConstraintReader(db_session).get_applicable_constraints(
            USER_ID,
            "USD",
        )


async def test_budget_reader_keeps_active_user_budget_when_department_path_is_inactive(
    db_session: AsyncSession,
) -> None:
    member = OrganizationMemberModel(
        id=UUID("50000000-0000-0000-0000-000000000003"),
        identity_user_id=USER_ID,
        is_active=True,
    )
    department = DepartmentModel(id=DEPARTMENT_ID, name="Engineering", is_active=False)
    db_session.add_all([member, department])
    await db_session.flush()
    db_session.add(
        DepartmentMembershipModel(
            member_id=member.id,
            department_id=DEPARTMENT_ID,
            is_active=True,
        )
    )
    db_session.add_all(
        [
            BudgetLimitModel(
                id=UUID("40000000-0000-0000-0000-000000000011"),
                owner_type="USER",
                user_id=USER_ID,
                department_id=None,
                amount=Decimal("500.00"),
                currency="USD",
                is_active=True,
            ),
            BudgetLimitModel(
                id=UUID("40000000-0000-0000-0000-000000000012"),
                owner_type="DEPARTMENT",
                user_id=None,
                department_id=DEPARTMENT_ID,
                amount=Decimal("1000.00"),
                currency="USD",
                is_active=True,
            ),
        ]
    )
    await db_session.commit()

    constraints = await SqlAlchemyBudgetConstraintReader(db_session).get_applicable_constraints(
        USER_ID,
        "USD",
    )

    assert [(item.owner_type, item.available.amount) for item in constraints] == [
        ("USER", Decimal("500.00"))
    ]


async def test_catalog_reader_rejects_ambiguous_active_offers(
    db_session: AsyncSession,
) -> None:
    product = ProductModel(
        id=UUID("10000000-0000-0000-0000-000000000020"),
        name="Docking station",
        is_active=True,
    )
    first_vendor = VendorModel(
        id=UUID("20000000-0000-0000-0000-000000000020"),
        name="First vendor",
        is_active=True,
    )
    second_vendor = VendorModel(
        id=UUID("20000000-0000-0000-0000-000000000021"),
        name="Second vendor",
        is_active=True,
    )
    db_session.add_all([product, first_vendor, second_vendor])
    await db_session.flush()
    db_session.add_all(
        [
            TrustedOfferModel(
                id=UUID("30000000-0000-0000-0000-000000000020"),
                product_id=product.id,
                vendor_id=first_vendor.id,
                unit_price_amount=Decimal("80.00"),
                currency="USD",
                available_quantity=5,
                is_active=True,
            ),
            TrustedOfferModel(
                id=UUID("30000000-0000-0000-0000-000000000021"),
                product_id=product.id,
                vendor_id=second_vendor.id,
                unit_price_amount=Decimal("70.00"),
                currency="USD",
                available_quantity=8,
                is_active=True,
            ),
        ]
    )
    await db_session.commit()

    with pytest.raises(DomainValidationError, match="explicit offer selection is required"):
        await SqlAlchemyTrustedCatalogReader(db_session).find_item("Docking stations")
