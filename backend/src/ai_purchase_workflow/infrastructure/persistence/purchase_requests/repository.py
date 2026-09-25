from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus
from ai_purchase_workflow.infrastructure.persistence.models import PurchaseRequestModel
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.loader import (
    PurchaseRequestAggregateLoader,
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
        loader: PurchaseRequestAggregateLoader | None = None,
    ) -> None:
        resolved_mapper = mapper or PurchaseRequestPersistenceMapper()
        self._session = session
        self._mapper = resolved_mapper
        self._related_writer = related_writer or PurchaseRequestRelatedRecordWriter()
        self._loader = loader or PurchaseRequestAggregateLoader(session, resolved_mapper)

    async def add(self, request: PurchaseRequest) -> None:
        self._session.add(self._mapper.to_model(request))
        await self._session.flush()
        self._related_writer.add_to_session(self._session, request)
        await self._session.commit()

    async def save(self, request: PurchaseRequest) -> None:
        model = await self._session.get(PurchaseRequestModel, request.id)
        if model is None:
            raise LookupError(f"Purchase request {request.id} was not found.")
        self._mapper.update_model(model, request)
        await self._related_writer.add_missing_to_session(self._session, request)
        await self._session.commit()

    async def get(self, request_id: UUID) -> PurchaseRequest | None:
        model = await self._session.get(PurchaseRequestModel, request_id)
        if model is None:
            return None
        return await self._loader.load_one(model)

    async def list(self, status: RequestStatus | None = None) -> tuple[PurchaseRequest, ...]:
        statement = select(PurchaseRequestModel)
        if status is not None:
            statement = statement.where(PurchaseRequestModel.status == status.value)
        statement = statement.order_by(PurchaseRequestModel.created_at, PurchaseRequestModel.id)
        models = tuple((await self._session.scalars(statement)).all())
        return await self._loader.load_many(models)
