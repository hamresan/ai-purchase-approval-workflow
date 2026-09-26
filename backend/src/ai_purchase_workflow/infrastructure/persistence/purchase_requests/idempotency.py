from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.purchase_requests.idempotency import (
    IdempotentPurchaseRequestCreator,
)
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest
from ai_purchase_workflow.infrastructure.persistence.models import PurchaseRequestIdempotencyModel
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.idempotency_reader import (
    IdempotentPurchaseRequestReader,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.mapper import (
    PurchaseRequestPersistenceMapper,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.writer import (
    PurchaseRequestRelatedRecordWriter,
)


class SqlAlchemyIdempotentPurchaseRequestCreator(IdempotentPurchaseRequestCreator):
    def __init__(
        self,
        session: AsyncSession,
        mapper: PurchaseRequestPersistenceMapper,
        writer: PurchaseRequestRelatedRecordWriter,
        reader: IdempotentPurchaseRequestReader,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._writer = writer
        self._reader = reader

    async def create(self, key: str, request: PurchaseRequest) -> PurchaseRequest:
        existing = await self._reader.get(key)
        if existing is not None:
            return existing

        self._session.add(self._mapper.to_model(request))
        await self._session.flush()
        self._writer.add_to_session(self._session, request)
        self._session.add(PurchaseRequestIdempotencyModel(key=key, request_id=request.id))
        try:
            await self._session.commit()
            return request
        except IntegrityError:
            await self._session.rollback()
            existing = await self._reader.get(key)
            if existing is None:
                raise
            return existing
