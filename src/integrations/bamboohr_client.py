"""Mock BambooHR adapter."""

from __future__ import annotations

import time
import uuid
from typing import Any

from config.settings import get_settings
from src.integrations.base import IntegrationAdapter
from src.models.case import ProposedAction


class BambooHRAdapter(IntegrationAdapter):
    name = "bamboohr"

    def execute(self, action: ProposedAction, case_id: str) -> dict[str, Any]:
        settings = get_settings()
        time.sleep(settings.mock_integration_latency_seconds)
        return {
            "system": "BambooHR",
            "task_id": str(uuid.uuid4()),
            "template": action.payload.get("task_template", "generic"),
            "mock": True,
        }
