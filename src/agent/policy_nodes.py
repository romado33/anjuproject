"""Deterministic policy nodes (replace LLM routing + action planning)."""

from __future__ import annotations

from src.agent.state import GraphState
from src.models.case import CaseStatus
from src.policy.engine import (
    build_actions_from_policy,
    compute_risk_tier,
    rag_influence_note,
    route_from_policy,
)


def policy_router_node(state: GraphState) -> dict:
    case = state["case"]
    if not case.classification:
        raise RuntimeError("Classification required before policy routing")
    case.status = CaseStatus.ROUTING
    case.routing = route_from_policy(case)
    case.append_audit(
        "policy_routing",
        case.routing.reasoning,
        team=case.routing.target_team,
        sla_hours=case.routing.sla_hours,
    )
    case.status = CaseStatus.PLANNING
    return {"case": case}


def policy_action_node(state: GraphState) -> dict:
    case = state["case"]
    if not (case.classification and case.routing):
        raise RuntimeError("Classification and routing required before actions")
    case.risk_tier = compute_risk_tier(case).value
    case.rag_influence_summary = rag_influence_note(case)
    case.proposed_actions = build_actions_from_policy(case)
    for a in case.proposed_actions:
        case.append_audit(
            "action_proposed",
            f"{a.action_type.value}: {a.title}",
            action_id=a.id,
        )
    case.status = CaseStatus.PENDING_APPROVAL
    return {"case": case}
