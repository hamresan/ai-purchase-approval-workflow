from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest
from ai_purchase_workflow.infrastructure.persistence.models import (
    ApprovalDecisionModel,
    AuditEntryModel,
    DraftOrderModel,
    PurchaseRequestModel,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.mapper import (
    PurchaseRequestPersistenceMapper,
)


class PurchaseRequestAggregateLoader:
    def __init__(
        self,
        session: AsyncSession,
        mapper: PurchaseRequestPersistenceMapper | None = None,
    ) -> None:
        self._session = session
        self._mapper = mapper or PurchaseRequestPersistenceMapper()

    async def load_one(self, model: PurchaseRequestModel) -> PurchaseRequest:
        results = await self.load_many((model,))
        return results[0]

    async def load_many(
        self,
        models: tuple[PurchaseRequestModel, ...],
    ) -> tuple[PurchaseRequest, ...]:
        if not models:
            return ()

        request_ids = tuple(model.id for model in models)
        drafts = (
            await self._session.scalars(
                select(DraftOrderModel).where(DraftOrderModel.request_id.in_(request_ids))
            )
        ).all()
        decisions = (
            await self._session.scalars(
                select(ApprovalDecisionModel)
                .where(ApprovalDecisionModel.request_id.in_(request_ids))
                .order_by(
                    ApprovalDecisionModel.request_id,
                    ApprovalDecisionModel.decided_at,
                    ApprovalDecisionModel.id,
                )
            )
        ).all()
        audits = (
            await self._session.scalars(
                select(AuditEntryModel)
                .where(AuditEntryModel.request_id.in_(request_ids))
                .order_by(AuditEntryModel.request_id, AuditEntryModel.sequence)
            )
        ).all()

        drafts_by_request = {draft.request_id: draft for draft in drafts}
        decisions_by_request = {decision.request_id: decision for decision in decisions}
        audits_by_request: dict[UUID, list[AuditEntryModel]] = {}
        for audit in audits:
            audits_by_request.setdefault(audit.request_id, []).append(audit)

        return tuple(
            self._mapper.to_domain(
                model,
                drafts_by_request.get(model.id),
                decisions_by_request.get(model.id),
                tuple(audits_by_request.get(model.id, [])),
            )
            for model in models
        )
