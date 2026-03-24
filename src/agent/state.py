"""LangGraph shared state."""

from __future__ import annotations

from typing import TypedDict

from src.models.case import CaseRecord


class GraphState(TypedDict):
    """State passed between agent nodes."""

    case: CaseRecord
