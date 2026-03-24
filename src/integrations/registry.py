"""Maps action types to adapters (AnjuBUS-style registry)."""

from __future__ import annotations

from typing import Any

from src.integrations.bamboohr_client import BambooHRAdapter
from src.integrations.base import IntegrationAdapter
from src.integrations.jira_client import JiraAdapter
from src.integrations.netsuite_client import NetSuiteAdapter
from src.integrations.salesforce_client import SalesforceAdapter
from src.integrations.teams_client import TeamsAdapter
from src.integrations.wiki_client import WikiChecklistAdapter
from src.models.case import ActionType, ProposedAction


class IntegrationRegistry:
    """Dispatch proposed actions to the correct adapter."""

    def __init__(self) -> None:
        self._map: dict[ActionType, IntegrationAdapter] = {
            ActionType.JIRA_ISSUE: JiraAdapter(),
            ActionType.TEAMS_NOTIFICATION: TeamsAdapter(),
            ActionType.SALESFORCE_ACTIVITY: SalesforceAdapter(),
            ActionType.NETSUITE_TIME_OR_PROJECT: NetSuiteAdapter(),
            ActionType.BAMBOOHR_TASK: BambooHRAdapter(),
            ActionType.IMPLEMENTATION_CHECKLIST: WikiChecklistAdapter(),
        }

    def dispatch(self, action: ProposedAction, case_id: str) -> dict[str, Any]:
        adapter = self._map.get(action.action_type)
        if adapter is None:
            return {
                "error": "no_adapter",
                "action_type": action.action_type.value,
            }
        return adapter.execute(action, case_id)

    def describe(self) -> dict[str, list[str]]:
        return {k.value: v.capabilities() for k, v in self._map.items()}


_default_registry: IntegrationRegistry | None = None


def get_default_registry() -> IntegrationRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = IntegrationRegistry()
    return _default_registry
