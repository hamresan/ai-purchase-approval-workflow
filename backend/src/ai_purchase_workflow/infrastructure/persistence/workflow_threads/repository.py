from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.workflows import WorkflowThreadRepository
from ai_purchase_workflow.infrastructure.persistence.models import WorkflowThreadModel


class SqlAlchemyWorkflowThreadRepository(WorkflowThreadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def bind(self, request_id: UUID, thread_id: str) -> None:
        existing = await self._session.get(WorkflowThreadModel, request_id)
        if existing is not None:
            if existing.thread_id != thread_id:
                raise ValueError("Purchase request is already bound to another workflow thread.")
            return
        self._session.add(
            WorkflowThreadModel(
                request_id=request_id,
                thread_id=thread_id,
                created_at=datetime.now(UTC),
            )
        )
        await self._session.commit()

    async def get_thread_id(self, request_id: UUID) -> str | None:
        model = await self._session.get(WorkflowThreadModel, request_id)
        return None if model is None else model.thread_id
