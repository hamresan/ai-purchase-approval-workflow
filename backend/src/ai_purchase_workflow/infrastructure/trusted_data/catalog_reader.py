from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.trusted_data import TrustedCatalogItem, TrustedCatalogReader
from ai_purchase_workflow.domain.purchase_requests import DomainValidationError, Money
from ai_purchase_workflow.infrastructure.trusted_data.models import (
    ProductModel,
    TrustedOfferModel,
    VendorModel,
)
from ai_purchase_workflow.infrastructure.trusted_tools.catalog_item_matcher import (
    CatalogItemMatcher,
)


class SqlAlchemyTrustedCatalogReader(TrustedCatalogReader):
    def __init__(self, session: AsyncSession, matcher: CatalogItemMatcher | None = None) -> None:
        self._session = session
        self._matcher = matcher or CatalogItemMatcher()

    async def find_item(self, description: str) -> TrustedCatalogItem:
        rows = (
            await self._session.execute(
                select(ProductModel, TrustedOfferModel, VendorModel)
                .join(TrustedOfferModel, TrustedOfferModel.product_id == ProductModel.id)
                .join(VendorModel, VendorModel.id == TrustedOfferModel.vendor_id)
                .where(
                    ProductModel.is_active.is_(True),
                    TrustedOfferModel.is_active.is_(True),
                    VendorModel.is_active.is_(True),
                )
            )
        ).all()
        matches = [
            (product, offer, vendor)
            for product, offer, vendor in rows
            if self._matcher.matches(description, product.name)
        ]
        if not matches:
            raise DomainValidationError(f"No trusted vendor data is available for {description}.")
        product, offer, vendor = min(
            matches,
            key=lambda row: (row[1].unit_price_amount, row[2].name, str(row[1].id)),
        )
        return TrustedCatalogItem(
            product_id=product.id,
            description=product.name,
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            unit_price=Money(offer.unit_price_amount, offer.currency),
            available_quantity=offer.available_quantity,
        )
