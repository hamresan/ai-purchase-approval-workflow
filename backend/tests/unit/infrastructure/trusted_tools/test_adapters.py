import pytest

from ai_purchase_workflow.infrastructure.trusted_tools.adapters import FixtureCatalogReader


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "description",
    [
        "Laptop stand",
        "laptop stand",
        "LAPTOP STAND",
        "  Laptop   stand  ",
        "laptop stands",
        "Laptop Stands",
    ],
)
async def test_fixture_catalog_reader_normalizes_description_for_lookup(description: str) -> None:
    item = await FixtureCatalogReader().find_item(description)

    assert item.description == "Laptop stand"
    assert item.vendor == "Acme"
