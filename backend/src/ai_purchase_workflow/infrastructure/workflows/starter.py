from ai_purchase_workflow.application.purchase_requests.workflow_submission import (
    PurchaseRequestWorkflowStarter,
    PurchaseRequestWorkflowStartResult,
)
from ai_purchase_workflow.infrastructure.workflows.runner import PurchaseRequestWorkflowRunner


class LangGraphPurchaseRequestWorkflowStarter(PurchaseRequestWorkflowStarter):
    def __init__(self, runner: PurchaseRequestWorkflowRunner) -> None:
        self._runner = runner

    async def start(self, free_text: str) -> PurchaseRequestWorkflowStartResult:
        result = await self._runner.execute(free_text)
        return PurchaseRequestWorkflowStartResult(
            purchase_request_id=result.purchase_request_id,
            review_reason=result.review_reason,
        )
