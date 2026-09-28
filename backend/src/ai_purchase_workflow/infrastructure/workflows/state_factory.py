from uuid import UUID, uuid4

from ai_purchase_workflow.infrastructure.workflows.state import PurchaseRequestWorkflowState


class PurchaseRequestWorkflowStateFactory:
    def create(
        self,
        free_text: str,
        *,
        requester_name: str | None = None,
        requester_user_id: UUID | None = None,
        checkpoint_id: str | None = None,
    ) -> PurchaseRequestWorkflowState:
        return {
            "workflow_id": checkpoint_id or str(uuid4()),
            "messages": (free_text,),
            "free_text": free_text,
            "requester_name": requester_name,
            "requester_user_id": requester_user_id,
            "status": "started",
            "tool_results": (),
        }
