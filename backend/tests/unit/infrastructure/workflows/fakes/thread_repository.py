from uuid import UUID

from ai_purchase_workflow.application.workflows import WorkflowThreadRepository


class InMemoryWorkflowThreadRepository(WorkflowThreadRepository):
    def __init__(self) -> None:
        self.thread_ids: dict[UUID, str] = {}

    async def bind(self, request_id: UUID, thread_id: str) -> None:
        existing = self.thread_ids.get(request_id)
        if existing is not None and existing != thread_id:
            raise ValueError("Purchase request is already bound to another workflow thread.")
        self.thread_ids[request_id] = thread_id

    async def get_thread_id(self, request_id: UUID) -> str | None:
        return self.thread_ids.get(request_id)
