from typing import Protocol
from uuid import UUID


class PurchaseRequestWorkflowGateway(Protocol):
    async def resume_approved(self, request_id: UUID) -> None: ...

    async def resume_rejected(self, request_id: UUID) -> None: ...
