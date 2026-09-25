from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.approval import (
    PurchaseRequestWorkflowGateway,
)


class FakePurchaseRequestWorkflowGateway(PurchaseRequestWorkflowGateway):
    def __init__(self) -> None:
        self.approved_request_ids: list[UUID] = []
        self.rejected_request_ids: list[UUID] = []

    async def resume_approved(self, request_id: UUID) -> None:
        self.approved_request_ids.append(request_id)

    async def resume_rejected(self, request_id: UUID) -> None:
        self.rejected_request_ids.append(request_id)
