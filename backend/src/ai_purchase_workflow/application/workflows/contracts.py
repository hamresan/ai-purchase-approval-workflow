from typing import Protocol
from uuid import UUID


class WorkflowThreadRepository(Protocol):
    async def bind(self, request_id: UUID, thread_id: str) -> None: ...

    async def get_thread_id(self, request_id: UUID) -> str | None: ...
