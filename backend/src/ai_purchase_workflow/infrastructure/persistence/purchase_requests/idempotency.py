from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.purchase_requests.idempotency import (
    PurchaseRequestIdempotencyStore,
)
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest
from ai_purchase_workflow.infrastructure.persistence.models import (
    PurchaseRequestIdempotencyModel,
    PurchaseRequestModel,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.loader import (
    PurchaseRequestAggregateLoader,
)


class SqlAlchemyPurchaseRequestIdempotencyStore(PurchaseRequestIdempotencyStore):
    def __init__(self, session: AsyncSession, loader: PurchaseRequestAggregateLoader) -> None:
        self._session = session
        self._loader = loader

    async def get(self, key: str) -> PurchaseRequest | None:
        model = await self._session.scalar(
            select(PurchaseRequestModel)
            .join(
                PurchaseRequestIdempotencyModel,
                PurchaseRequestIdempotencyModel.request_id == PurchaseRequestModel.id,
            )
            .where(PurchaseRequestIdempotencyModel.key == key)
        )
        return None if model is None else await self._loader.load_one(model)

    async def bind(self, key: str, request: PurchaseRequest) -> PurchaseRequest:
        self._session.add(PurchaseRequestIdempotencyModel(key=key, request_id=request.id))
        try:
            await self._session.commit()
            return request
        except IntegrityError:
            await self._session.rollback()
            existing = await self.get(key)
            if existing is None:
                raise
            return existing
