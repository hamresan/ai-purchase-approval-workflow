from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ProductRecord:
    id: UUID
    name: str
    is_active: bool


class ProductRepository(Protocol):
    async def list_products(self) -> tuple[ProductRecord, ...]: ...
    async def create_product(self, name: str) -> ProductRecord: ...
    async def update_product(
        self, product_id: UUID, name: str, is_active: bool
    ) -> ProductRecord | None: ...


class ManageProducts:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    async def list_products(self) -> tuple[ProductRecord, ...]:
        return await self._repository.list_products()

    async def create_product(self, name: str) -> ProductRecord:
        return await self._repository.create_product(name)

    async def update_product(
        self, product_id: UUID, name: str, is_active: bool
    ) -> ProductRecord | None:
        return await self._repository.update_product(product_id, name, is_active)
