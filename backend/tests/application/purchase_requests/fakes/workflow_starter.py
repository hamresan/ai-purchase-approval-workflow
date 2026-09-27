from ai_purchase_workflow.application.purchase_requests import (
    PurchaseRequestWorkflowStartResult,
)


class FakePurchaseRequestWorkflowStarter:
    def __init__(self, result: PurchaseRequestWorkflowStartResult) -> None:
        self.result = result
        self.free_texts: list[str] = []

    async def start(self, free_text: str) -> PurchaseRequestWorkflowStartResult:
        self.free_texts.append(free_text)
        return self.result
