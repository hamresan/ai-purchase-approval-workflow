from ai_purchase_workflow.infrastructure.trusted_tools import FixtureOrderGateway


def test_fixture_order_gateway_remains_available_for_submission_boundary() -> None:
    assert FixtureOrderGateway is not None
