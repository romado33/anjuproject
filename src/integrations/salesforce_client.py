"""Mock Salesforce adapter (Salesforce-flavored payloads)."""

from __future__ import annotations

import time
import uuid
from typing import Any

from config.settings import get_settings
from src.integrations.base import IntegrationAdapter
from src.models.case import ProposedAction


class SalesforceAdapter(IntegrationAdapter):
    name = "salesforce"

    def execute(self, action: ProposedAction, case_id: str) -> dict[str, Any]:
        settings = get_settings()
        time.sleep(settings.mock_integration_latency_seconds)
        return {
            "system": "Salesforce",
            "object": action.payload.get("object", "Task"),
            "record_id": f"00T{uuid.uuid4().hex[:15].upper()}",
            "status": "created",
            "mock": True,
        }
