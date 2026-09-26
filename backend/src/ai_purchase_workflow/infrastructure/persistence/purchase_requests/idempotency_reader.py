from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest
from ai_purchase_workflow.infrastructure.persistence.models import (
    PurchaseRequestIdempotencyModel,
    PurchaseRequestModel,
)
from ai_purchase_workflow.infrastructure.persistence.purchase_requests.loader import (
    PurchaseRequestAggregateLoader,
)


class IdempotentPurchaseRequestReader:
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
