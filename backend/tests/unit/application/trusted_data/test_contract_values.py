from decimal import Decimal
from uuid import UUID

from ai_purchase_workflow.application.trusted_data import BudgetConstraint, TrustedCatalogItem
from ai_purchase_workflow.domain.purchase_requests import Money


def test_budget_constraint_preserves_owner_and_money() -> None:
    owner_id = UUID("11111111-1111-1111-1111-111111111111")

    constraint = BudgetConstraint(
        owner_type="USER",
        owner_id=owner_id,
        available=Money(Decimal("500.00"), "USD"),
    )

    assert constraint.owner_type == "USER"
    assert constraint.owner_id == owner_id
    assert constraint.available == Money(Decimal("500.00"), "USD")


def test_trusted_catalog_item_preserves_trusted_offer_data() -> None:
    product_id = UUID("11111111-1111-1111-1111-111111111111")
    vendor_id = UUID("22222222-2222-2222-2222-222222222222")

    item = TrustedCatalogItem(
        product_id=product_id,
        description="Laptop stand",
        vendor_id=vendor_id,
        vendor_name="Acme",
        unit_price=Money(Decimal("35.00"), "USD"),
        available_quantity=10,
    )

    assert item.product_id == product_id
    assert item.vendor_id == vendor_id
    assert item.vendor_name == "Acme"
    assert item.available_quantity == 10
