from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.mapper import (
    PurchaseRequestRelatedRecordMapper,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.synchronizers import (
    ApprovalDecisionSynchronizer,
    AuditEntrySynchronizer,
    DraftOrderSynchronizer,
)


class PurchaseRequestRelatedRecordWriter:
    def __init__(self, mapper: PurchaseRequestRelatedRecordMapper | None = None) -> None:
        self._mapper = mapper or PurchaseRequestRelatedRecordMapper()
        self._drafts = DraftOrderSynchronizer(self._mapper)
        self._decisions = ApprovalDecisionSynchronizer(self._mapper)
        self._audits = AuditEntrySynchronizer(self._mapper)

    def add_to_session(self, session: AsyncSession, request: PurchaseRequest) -> None:
        if request.draft_order is not None:
            session.add(self._mapper.to_draft_model(request.draft_order))
        if request.approval_decision is not None:
            session.add(self._mapper.to_decision_model(request.approval_decision))
        for sequence, audit in enumerate(request.audit_entries, start=1):
            session.add(self._mapper.to_audit_model(audit, sequence))

    async def sync_to_session(
        self,
        session: AsyncSession,
        request: PurchaseRequest,
    ) -> None:
        await self._drafts.sync(session, request)
        await self._decisions.sync(session, request)
        await self._audits.sync(session, request)
