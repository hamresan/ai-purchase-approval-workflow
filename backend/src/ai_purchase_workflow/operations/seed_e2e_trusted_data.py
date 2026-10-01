"""Seed deterministic trusted data for the isolated Docker E2E test environment."""

import asyncio
from decimal import Decimal
from uuid import UUID

from ai_purchase_workflow.composition_root.settings import get_settings
from ai_purchase_workflow.infrastructure.persistence import create_session_factory
from ai_purchase_workflow.infrastructure.trusted_data.models import (
    BudgetLimitModel,
    ProductModel,
    TrustedOfferModel,
    VendorModel,
)

PRODUCT_ID = UUID("a0000000-0000-0000-0000-000000000001")
VENDOR_ID = UUID("b0000000-0000-0000-0000-000000000001")
OFFER_ID = UUID("c0000000-0000-0000-0000-000000000001")
BUDGET_ID = UUID("d0000000-0000-0000-0000-000000000001")
REQUESTER_ID = UUID("11111111-1111-1111-1111-111111111111")


async def seed() -> None:
    settings = get_settings()
    if settings.app_env != "test":
        raise RuntimeError("E2E trusted-data seeding is restricted to APP_ENV=test.")

    session_factory = create_session_factory(settings.database_url)
    async with session_factory() as session:
        product = await session.get(ProductModel, PRODUCT_ID)
        if product is None:
            product = ProductModel(id=PRODUCT_ID, name="Laptop stand", is_active=True)
            session.add(product)
        else:
            product.name = "Laptop stand"
            product.is_active = True

        vendor = await session.get(VendorModel, VENDOR_ID)
        if vendor is None:
            vendor = VendorModel(id=VENDOR_ID, name="Acme", is_active=True)
            session.add(vendor)
        else:
            vendor.name = "Acme"
            vendor.is_active = True

        await session.flush()

        offer = await session.get(TrustedOfferModel, OFFER_ID)
        if offer is None:
            offer = TrustedOfferModel(
                id=OFFER_ID,
                product_id=PRODUCT_ID,
                vendor_id=VENDOR_ID,
                unit_price_amount=Decimal("35.00"),
                currency="USD",
                available_quantity=10,
                is_active=True,
            )
            session.add(offer)
        else:
            offer.product_id = PRODUCT_ID
            offer.vendor_id = VENDOR_ID
            offer.unit_price_amount = Decimal("35.00")
            offer.currency = "USD"
            offer.available_quantity = 10
            offer.is_active = True

        budget = await session.get(BudgetLimitModel, BUDGET_ID)
        if budget is None:
            budget = BudgetLimitModel(
                id=BUDGET_ID,
                owner_type="USER",
                user_id=REQUESTER_ID,
                department_id=None,
                amount=Decimal("500.00"),
                currency="USD",
                is_active=True,
            )
            session.add(budget)
        else:
            budget.owner_type = "USER"
            budget.user_id = REQUESTER_ID
            budget.department_id = None
            budget.amount = Decimal("500.00")
            budget.currency = "USD"
            budget.is_active = True

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
