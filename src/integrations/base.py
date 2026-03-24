"""Adapter contract for external systems (mock or real)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.models.case import ProposedAction


class IntegrationAdapter(ABC):
    """AnjuBUS-inspired adapter: validate payload, execute, return audit-safe result."""

    name: str = "base"

    @abstractmethod
    def execute(self, action: ProposedAction, case_id: str) -> dict[str, Any]:
        """Return a JSON-serializable result for audit and UI."""

    def capabilities(self) -> list[str]:
        return [self.name]
