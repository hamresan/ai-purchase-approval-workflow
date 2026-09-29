from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.workflow_submission import (
    PurchaseRequestWorkflowStarter,
    PurchaseRequestWorkflowStartResult,
)
from ai_purchase_workflow.infrastructure.workflows.runner import PurchaseRequestWorkflowRunner


class LangGraphPurchaseRequestWorkflowStarter(PurchaseRequestWorkflowStarter):
    def __init__(self, runner: PurchaseRequestWorkflowRunner) -> None:
        self._runner = runner

    async def start(
        self,
        free_text: str,
        *,
        requester_name: str | None = None,
        requester_user_id: UUID | None = None,
    ) -> PurchaseRequestWorkflowStartResult:
        result = await self._runner.execute(
            free_text,
            requester_name=requester_name,
            requester_user_id=requester_user_id,
        )
        return PurchaseRequestWorkflowStartResult(
            purchase_request_id=result.purchase_request_id,
            review_reason=result.review_reason,
        )
