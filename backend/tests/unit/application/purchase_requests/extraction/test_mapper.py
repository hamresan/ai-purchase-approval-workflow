import pytest

from ai_purchase_workflow.application.purchase_requests.extraction import (
    MalformedModelOutputError,
    ModelResponse,
    StructuredOutputMapper,
)


def test_map_converts_structured_model_output() -> None:
    result = StructuredOutputMapper().map(
        ModelResponse(
            content={
                "schema_version": "1.0",
                "requester_name": "Dana",
                "items": [{"description": "Laptop stand", "quantity": 2}],
            }
        )
    )

    assert result.schema_version == "1.0"
    assert result.requester_name == "Dana"
    assert result.items[0].description == "Laptop stand"
    assert result.items[0].quantity == 2


@pytest.mark.parametrize(
    "content",
    [
        "not structured",
        {"schema_version": "1.0", "items": "invalid"},
        {"schema_version": "1.0", "items": [{"description": "Stand", "quantity": "2"}]},
    ],
)
def test_map_rejects_malformed_output(content: object) -> None:
    with pytest.raises(MalformedModelOutputError):
        StructuredOutputMapper().map(ModelResponse(content=content))


def test_map_rejects_forbidden_tool_request() -> None:
    response = ModelResponse(
        content={
            "schema_version": "1.0",
            "items": [{"description": "Laptop stand", "quantity": 1}],
            "tool_calls": [{"name": "submit_order"}],
        }
    )

    with pytest.raises(MalformedModelOutputError, match="forbidden fields: tool_calls"):
        StructuredOutputMapper().map(response)
