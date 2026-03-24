"""Mock adapter contract tests."""

from __future__ import annotations

import os

os.environ.pop("OPENAI_API_KEY", None)

from src.integrations.registry import get_default_registry
from src.models.case import ActionType, ProposedAction


def test_jira_dispatch() -> None:
    reg = get_default_registry()
    action = ProposedAction(
        action_type=ActionType.JIRA_ISSUE,
        target_system="Jira Cloud",
        title="Test",
        payload={"project_key": "ANJU"},
        reasoning="unit test",
    )
    out = reg.dispatch(action, "case-1")
    assert "issue_key" in out
    assert out.get("mock") is True
