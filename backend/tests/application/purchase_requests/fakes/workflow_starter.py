from uuid import UUID

from ai_purchase_workflow.application.purchase_requests import (
    PurchaseRequestWorkflowStarter,
    PurchaseRequestWorkflowStartResult,
)


class FakePurchaseRequestWorkflowStarter(PurchaseRequestWorkflowStarter):
    def __init__(self, result: PurchaseRequestWorkflowStartResult) -> None:
        self.result = result
        self.free_texts: list[str] = []
        self.requester_names: list[str | None] = []
        self.requester_user_ids: list[UUID | None] = []

    async def start(
        self,
        free_text: str,
        *,
        requester_name: str | None = None,
        requester_user_id: UUID | None = None,
    ) -> PurchaseRequestWorkflowStartResult:
        self.free_texts.append(free_text)
        self.requester_names.append(requester_name)
        self.requester_user_ids.append(requester_user_id)
        return self.result
