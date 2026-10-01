from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class VendorRecord:
    id: UUID
    name: str
    is_active: bool


class VendorRepository(Protocol):
    async def list_vendors(self) -> tuple[VendorRecord, ...]: ...
    async def create_vendor(self, name: str) -> VendorRecord: ...
    async def update_vendor(
        self, vendor_id: UUID, name: str, is_active: bool
    ) -> VendorRecord | None: ...


class ManageVendors:
    def __init__(self, repository: VendorRepository) -> None:
        self._repository = repository

    async def list_vendors(self) -> tuple[VendorRecord, ...]:
        return await self._repository.list_vendors()

    async def create_vendor(self, name: str) -> VendorRecord:
        return await self._repository.create_vendor(name)

    async def update_vendor(
        self, vendor_id: UUID, name: str, is_active: bool
    ) -> VendorRecord | None:
        return await self._repository.update_vendor(vendor_id, name, is_active)
