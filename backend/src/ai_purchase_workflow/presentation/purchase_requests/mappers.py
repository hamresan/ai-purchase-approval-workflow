from ai_purchase_workflow.application.purchase_requests import (
    CreatePurchaseItem,
    CreatePurchaseRequestCommand,
    EditPurchaseItem,
)
from ai_purchase_workflow.presentation.purchase_requests.schemas import (
    ApprovalBody,
    CreatePurchaseRequestBody,
)


class PurchaseRequestCommandMapper:
    @staticmethod
    def from_body(body: CreatePurchaseRequestBody) -> CreatePurchaseRequestCommand:
        return CreatePurchaseRequestCommand(
            requester_name=body.requester_name,
            items=tuple(
                CreatePurchaseItem(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price_amount=item.unit_price_amount,
                    currency=item.currency,
                    vendor=item.vendor,
                )
                for item in body.items
            ),
        )


class ApprovalCommandMapper:
    @staticmethod
    def edit_items(body: ApprovalBody) -> tuple[EditPurchaseItem, ...]:
        return tuple(
            EditPurchaseItem(description=item.description, quantity=item.quantity)
            for item in body.items or ()
        )
