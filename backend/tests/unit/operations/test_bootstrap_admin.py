from argparse import Namespace

import pytest

from ai_purchase_workflow.operations import bootstrap_admin


def test_parse_args_requires_mobile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["bootstrap_admin", "--mobile", "+96891234567"])

    args = bootstrap_admin.parse_args()

    assert args == Namespace(mobile="+96891234567")
