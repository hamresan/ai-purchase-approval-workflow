from ai_purchase_workflow.infrastructure.prompts import FilePromptTemplateReader


def test_read_loads_versioned_extraction_prompt() -> None:
    template = FilePromptTemplateReader().read("purchase_request_extraction", "v1")

    assert "schema version {schema_version}" in template
    assert "Never invent or infer price, vendor, budget" in template
    assert "Do not request or invoke tools." in template
