from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus
from ai_purchase_workflow.infrastructure.persistence.models import (
    ApprovalDecisionModel,
    AuditEntryModel,
    DraftOrderModel,
    PurchaseRequestModel,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.mapper import (
    PurchaseRequestPersistenceMapper,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.writer import (
    PurchaseRequestRelatedRecordWriter,
)


class SqlAlchemyPurchaseRequestRepository(PurchaseRequestRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: PurchaseRequestPersistenceMapper | None = None,
        related_writer: PurchaseRequestRelatedRecordWriter | None = None,
    ) -> None:
        self._session = session
        self._mapper = mapper or PurchaseRequestPersistenceMapper()
        self._related_writer = related_writer or PurchaseRequestRelatedRecordWriter()

    async def add(self, request: PurchaseRequest) -> None:
        self._session.add(self._mapper.to_model(request))
        self._related_writer.add_to_session(self._session, request)
        await self._session.commit()

    async def get(self, request_id: UUID) -> PurchaseRequest | None:
        model = await self._session.get(PurchaseRequestModel, request_id)
        if model is None:
            return None
        draft = await self._session.scalar(
            select(DraftOrderModel).where(DraftOrderModel.request_id == model.id)
        )
        decision = await self._session.scalar(
            select(ApprovalDecisionModel).where(ApprovalDecisionModel.request_id == model.id)
        )
        audits = tuple(
            (
                await self._session.scalars(
                    select(AuditEntryModel)
                    .where(AuditEntryModel.request_id == model.id)
                    .order_by(AuditEntryModel.sequence)
                )
            ).all()
        )
        return self._mapper.to_domain(model, draft, decision, audits)

    async def list(self, status: RequestStatus | None = None) -> tuple[PurchaseRequest, ...]:
        statement = select(PurchaseRequestModel)
        if status is not None:
            statement = statement.where(PurchaseRequestModel.status == status.value)
        statement = statement.order_by(PurchaseRequestModel.created_at, PurchaseRequestModel.id)
        models = (await self._session.scalars(statement)).all()
        requests: list[PurchaseRequest] = []
        for model in models:
            request = await self.get(model.id)
            if request is not None:
                requests.append(request)
        return tuple(requests)
