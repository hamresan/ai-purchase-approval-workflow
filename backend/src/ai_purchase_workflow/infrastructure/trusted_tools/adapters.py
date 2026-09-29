from ai_purchase_workflow.application.purchase_requests.trusted_tools import OrderGateway
from ai_purchase_workflow.domain.purchase_requests import DraftOrder


class FixtureOrderGateway(OrderGateway):
    async def submit(self, draft_order: DraftOrder) -> str:
        return f"fixture-order-{draft_order.id}"
