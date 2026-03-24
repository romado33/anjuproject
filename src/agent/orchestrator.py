"""LangGraph orchestration for the case router."""

from __future__ import annotations

from functools import partial

from langgraph.graph import END, START, StateGraph

from config.settings import get_settings
from src.agent.classifier import classify_node
from src.agent.context_gatherer import context_gatherer_node
from src.agent.offline import run_offline_pipeline
from src.agent.policy_nodes import policy_action_node, policy_router_node
from src.agent.state import GraphState
from src.models.case import CaseRecord, CaseStatus
from src.policy.restricted import analyze_restricted


def build_graph() -> StateGraph:
    """Compile classify → conditional RAG → deterministic policy route → policy actions."""
    settings = get_settings()
    graph = StateGraph(GraphState)
    graph.add_node("classify", partial(classify_node, settings=settings))
    graph.add_node("retrieve", context_gatherer_node)
    graph.add_node("route", policy_router_node)
    graph.add_node("plan", policy_action_node)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "route")
    graph.add_edge("route", "plan")
    graph.add_edge("plan", END)
    return graph.compile()


def run_agent_pipeline(case: CaseRecord) -> CaseRecord:
    """
    Run offline heuristics or full LLM+RAG pipeline.
    Terminal state: PENDING_APPROVAL (awaiting human gate).
    """
    settings = get_settings()

    analysis = analyze_restricted(case.text_for_llm())
    if analysis.is_restricted:
        case.restricted_mode = True
        case.restricted_signals = list(analysis.signals)
        case.llm_allowed = False
        case.append_audit(
            "restricted_gate",
            "Restricted-content signals detected; external LLM path disabled (demo). "
            "Deterministic classification and policy actions only.",
            signals=analysis.signals,
        )
        run_offline_pipeline(case)
        case.status = CaseStatus.PENDING_APPROVAL
        return case

    if settings.use_offline_mode():
        case.append_audit(
            "pipeline_mode",
            "Running offline deterministic pipeline (no OpenAI). "
            "Configure OPENAI_API_KEY and disable OFFLINE_DEMO for full agent.",
        )
        run_offline_pipeline(case)
        case.status = CaseStatus.PENDING_APPROVAL
        return case

    app = build_graph()
    out = app.invoke({"case": case})
    updated: CaseRecord = out["case"]
    # Low-confidence flag for UI (does not block pipeline)
    thr = settings.classification_confidence_threshold
    if (
        updated.classification
        and updated.classification.confidence < thr
    ):
        updated.append_audit(
            "confidence_flag",
            f"Confidence {updated.classification.confidence:.2f} below threshold {thr}.",
            threshold=thr,
        )
    return updated
