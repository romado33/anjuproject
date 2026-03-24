"""Deterministic policy: routing matrix, selective actions, conditional RAG, KB nudges."""

from __future__ import annotations

import os

os.environ["OFFLINE_DEMO"] = "true"
os.environ["OPENAI_API_KEY"] = ""

from src.models.case import (
    ActionType,
    CaseIntake,
    CaseRecord,
    Classification,
    IssueType,
    ProductLine,
    Urgency,
)
from src.policy.engine import (
    aggregate_operator_metrics,
    build_actions_from_policy,
    route_from_policy,
    should_retrieve_context,
)
from src.workflow.engine import CaseWorkflowEngine


def _case(
    text: str,
    classification: Classification,
    *,
    rag: list[dict] | None = None,
) -> CaseRecord:
    c = CaseRecord(intake=CaseIntake(request_text=text), classification=classification)
    if rag is not None:
        c.rag_context = rag
    c.routing = route_from_policy(c)
    return c


def test_simple_ta_data_path_omits_jira() -> None:
    c = _case(
        "ta scan data export question api low priority " * 2,
        Classification(
            product=ProductLine.TA_SCAN,
            issue_type=IssueType.DATA_QUESTION,
            urgency=Urgency.LOW,
            sentiment="neutral",
            confidence=0.55,
            reasoning="unit",
            keywords=[],
        ),
    )
    actions = build_actions_from_policy(c)
    types = {a.action_type for a in actions}
    assert ActionType.JIRA_ISSUE not in types
    assert ActionType.SALESFORCE_ACTIVITY in types
    assert ActionType.TEAMS_NOTIFICATION in types


def test_training_high_confidence_skips_rag() -> None:
    case = CaseRecord(
        intake=CaseIntake(request_text="user guide training for reports " * 2),
        classification=Classification(
            product=ProductLine.TRIALMASTER,
            issue_type=IssueType.TRAINING,
            urgency=Urgency.LOW,
            sentiment="neutral",
            confidence=0.8,
            reasoning="unit",
            keywords=[],
        ),
    )
    do_r, _reason = should_retrieve_context(case)
    assert do_r is False


def test_kb_nudge_irms_data_question_to_integrations() -> None:
    case = _case(
        "irms report data export question " * 2,
        Classification(
            product=ProductLine.IRMS_MAX,
            issue_type=IssueType.DATA_QUESTION,
            urgency=Urgency.MEDIUM,
            sentiment="neutral",
            confidence=0.7,
            reasoning="unit",
            keywords=[],
        ),
        rag=[{"document": "Veeva integration connector and AnjuBUS endpoint setup", "metadata": {}}],
    )
    assert case.routing is not None
    assert case.routing.target_team == "MI Integrations"
    assert "RAG influence" in case.routing.reasoning


def test_implementation_routes_to_professional_services() -> None:
    c = _case(
        "irms kickoff implementation onboarding signed contract " * 2,
        Classification(
            product=ProductLine.IRMS_MAX,
            issue_type=IssueType.IMPLEMENTATION,
            urgency=Urgency.MEDIUM,
            sentiment="neutral",
            confidence=0.72,
            reasoning="unit",
            keywords=[],
        ),
    )
    assert c.routing is not None
    assert c.routing.target_team == "Professional Services"
    assert "PS-MI-Onboarding" in c.routing.queue_name or "Onboarding" in c.routing.queue_name
    acts = build_actions_from_policy(c)
    assert any(a.action_type == ActionType.JIRA_ISSUE for a in acts)
    assert any("Epic" in str(a.payload.get("issue_type", "")) for a in acts)


def test_aggregate_operator_metrics_counts() -> None:
    from src.models.case import CaseRecord, CaseIntake

    minimal = CaseIntake(request_text="x" * 40, redact_pii=False)
    # Two synthetic records: one without LLM, one with proposed actions
    a = CaseRecord(intake=minimal, llm_allowed=False, proposed_actions=[])
    b = CaseRecord(intake=minimal, llm_allowed=True, proposed_actions=[])
    m = aggregate_operator_metrics([a, b])
    assert m["cases_without_external_llm"] == 1


def test_restricted_gate_disables_llm_path() -> None:
    engine = CaseWorkflowEngine()
    case = engine.start_case(
        CaseIntake(
            request_text=(
                "Confidential: patient MRN 998877 reported SAE; site #12 for NCT12345678 follow-up."
            ),
        )
    )
    assert case.restricted_mode is True
    assert case.llm_allowed is False
