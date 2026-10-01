from typing import Literal, cast

from ai_purchase_workflow.application.admin import (
    BudgetRecord,
    OfferRecord,
    ProductRecord,
    VendorRecord,
)
from ai_purchase_workflow.infrastructure.trusted_data.models import (
    BudgetLimitModel,
    ProductModel,
    TrustedOfferModel,
    VendorModel,
)


class AdminResourceMapper:
    @staticmethod
    def product(row: ProductModel) -> ProductRecord:
        return ProductRecord(row.id, row.name, row.is_active)

    @staticmethod
    def product_model(value: ProductRecord) -> ProductModel:
        return ProductModel(id=value.id, name=value.name, is_active=value.is_active)

    @staticmethod
    def vendor(row: VendorModel) -> VendorRecord:
        return VendorRecord(row.id, row.name, row.is_active)

    @staticmethod
    def vendor_model(value: VendorRecord) -> VendorModel:
        return VendorModel(id=value.id, name=value.name, is_active=value.is_active)

    @staticmethod
    def offer(row: TrustedOfferModel) -> OfferRecord:
        return OfferRecord(
            row.id,
            row.product_id,
            row.vendor_id,
            row.unit_price_amount,
            row.currency,
            row.available_quantity,
            row.is_active,
        )

    @staticmethod
    def offer_model(value: OfferRecord) -> TrustedOfferModel:
        return TrustedOfferModel(
            id=value.id,
            product_id=value.product_id,
            vendor_id=value.vendor_id,
            unit_price_amount=value.unit_price_amount,
            currency=value.currency,
            available_quantity=value.available_quantity,
            is_active=value.is_active,
        )

    @staticmethod
    def budget(row: BudgetLimitModel) -> BudgetRecord:
        owner_type = cast(Literal["USER", "DEPARTMENT"], row.owner_type)
        return BudgetRecord(
            row.id,
            owner_type,
            row.user_id,
            row.department_id,
            row.amount,
            row.currency,
            row.is_active,
        )

    @staticmethod
    def budget_model(value: BudgetRecord) -> BudgetLimitModel:
        return BudgetLimitModel(
            id=value.id,
            owner_type=value.owner_type,
            user_id=value.user_id,
            department_id=value.department_id,
            amount=value.amount,
            currency=value.currency,
            is_active=value.is_active,
        )
