"""Mock Microsoft Teams adapter."""

from __future__ import annotations

import time
import uuid
from typing import Any

from config.settings import get_settings
from src.integrations.base import IntegrationAdapter
from src.models.case import ProposedAction


class TeamsAdapter(IntegrationAdapter):
    name = "teams"

    def execute(self, action: ProposedAction, case_id: str) -> dict[str, Any]:
        settings = get_settings()
        time.sleep(settings.mock_integration_latency_seconds)
        return {
            "system": "Microsoft Teams",
            "delivery_status": "sent",
            "channel": action.payload.get("channel", "unknown"),
            "message_id": str(uuid.uuid4()),
            "mock": True,
        }
