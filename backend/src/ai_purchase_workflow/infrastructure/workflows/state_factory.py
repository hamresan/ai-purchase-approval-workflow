from uuid import uuid4

from ai_purchase_workflow.infrastructure.workflows.state import PurchaseRequestWorkflowState


class PurchaseRequestWorkflowStateFactory:
    def create(
        self,
        free_text: str,
        *,
        checkpoint_id: str | None = None,
    ) -> PurchaseRequestWorkflowState:
        return {
            "workflow_id": checkpoint_id or str(uuid4()),
            "messages": (free_text,),
            "free_text": free_text,
            "status": "started",
            "tool_results": (),
        }
