from ai_purchase_workflow.infrastructure.workflows.state import PurchaseRequestWorkflowState


class ResumeOnlyExtractNode:
    async def __call__(
        self,
        state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState:
        del state
        raise RuntimeError("Extraction cannot run while resuming an existing workflow.")


class ResumeOnlyPrepareNode:
    async def __call__(
        self,
        state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState:
        del state
        raise RuntimeError("Preparation cannot run while resuming an existing workflow.")
