"""Mock Jira Cloud adapter."""

from __future__ import annotations

import time
import uuid
from typing import Any

from config.settings import get_settings
from src.integrations.base import IntegrationAdapter
from src.models.case import ProposedAction


class JiraAdapter(IntegrationAdapter):
    name = "jira"

    def execute(self, action: ProposedAction, case_id: str) -> dict[str, Any]:
        settings = get_settings()
        time.sleep(settings.mock_integration_latency_seconds)
        key = f"ANJU-{1000 + (hash(case_id) % 9000)}"
        return {
            "system": "Jira Cloud",
            "issue_key": key,
            "url": f"https://example-jira.example.com/browse/{key}",
            "payload_echo": action.payload,
            "mock": True,
            "correlation_id": str(uuid.uuid4()),
        }
