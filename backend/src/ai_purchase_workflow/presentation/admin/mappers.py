from ai_purchase_workflow.application.admin import (
    BudgetRecord,
    BudgetValues,
    DepartmentRecord,
    OfferRecord,
    OfferValues,
    ProductRecord,
    RoleAssignment,
    VendorRecord,
)
from ai_purchase_workflow.presentation.admin.resource_schemas import (
    BudgetBody,
    BudgetResponse,
    OfferBody,
    OfferResponse,
    ProductResponse,
    RoleAssignmentResponse,
    VendorResponse,
)
from ai_purchase_workflow.presentation.admin.schemas import DepartmentResponse


class AdminMapper:
    @staticmethod
    def department_response(record: DepartmentRecord) -> DepartmentResponse:
        return DepartmentResponse(id=record.id, name=record.name, is_active=record.is_active)

    @staticmethod
    def product_response(record: ProductRecord) -> ProductResponse:
        return ProductResponse(id=record.id, name=record.name, is_active=record.is_active)

    @staticmethod
    def vendor_response(record: VendorRecord) -> VendorResponse:
        return VendorResponse(id=record.id, name=record.name, is_active=record.is_active)

    @staticmethod
    def role_response(record: RoleAssignment) -> RoleAssignmentResponse:
        return RoleAssignmentResponse(user_id=record.user_id, roles=set(record.roles))

    @staticmethod
    def offer_values(body: OfferBody) -> OfferValues:
        return OfferValues(
            body.product_id,
            body.vendor_id,
            body.unit_price_amount,
            body.currency,
            body.available_quantity,
            body.is_active,
        )

    @staticmethod
    def offer_response(record: OfferRecord) -> OfferResponse:
        return OfferResponse(
            id=record.id,
            product_id=record.product_id,
            vendor_id=record.vendor_id,
            unit_price_amount=format(record.unit_price_amount, ".2f"),
            currency=record.currency,
            available_quantity=record.available_quantity,
            is_active=record.is_active,
        )

    @staticmethod
    def budget_values(body: BudgetBody) -> BudgetValues:
        return BudgetValues(
            body.owner_type,
            body.user_id,
            body.department_id,
            body.amount,
            body.currency,
            body.is_active,
        )

    @staticmethod
    def budget_response(record: BudgetRecord) -> BudgetResponse:
        return BudgetResponse(
            id=record.id,
            owner_type=record.owner_type,
            user_id=record.user_id,
            department_id=record.department_id,
            amount=format(record.amount, ".2f"),
            currency=record.currency,
            is_active=record.is_active,
        )
