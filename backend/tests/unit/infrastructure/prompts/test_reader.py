from ai_purchase_workflow.infrastructure.prompts import FilePromptTemplateReader


def test_read_loads_versioned_extraction_prompt() -> None:
    template = FilePromptTemplateReader().read("purchase_request_extraction", "v1")

    assert "schema version {schema_version}" in template
    assert "Never invent or infer requester names, price, vendor, budget" in template
    assert "Item quantity must be a positive JSON integer, never text." in template
    assert "Use null when requester_name is not explicitly stated." in template
    assert "When human review is not needed, set review_reason to null." in template
    assert "Do not request or invoke tools." in template
