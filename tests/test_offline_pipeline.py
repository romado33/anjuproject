"""Offline pipeline tests (no OpenAI key required)."""

from __future__ import annotations

import os

import pytest

os.environ["OFFLINE_MODE"] = "true"
os.environ["OPENAI_API_KEY"] = ""

from src.models.case import CaseIntake, CaseStatus, ProductLine
from src.workflow.engine import CaseWorkflowEngine


def test_offline_end_to_end() -> None:
    engine = CaseWorkflowEngine()
    intake = CaseIntake(
        request_text=(
            "Our TrialMaster export fails for large datasets in Phase III. "
            "This is urgent for SDTM delivery."
        )
    )
    case = engine.start_case(intake)
    assert case.status == CaseStatus.PENDING_APPROVAL
    assert case.classification is not None
    assert case.classification.product == ProductLine.TRIALMASTER
    assert case.routing is not None
    assert len(case.proposed_actions) >= 1

    decisions = []
    from src.models.case import ApprovalDecision

    for a in case.proposed_actions:
        decisions.append(
            ApprovalDecision(action_id=a.id, decision="approved", reviewer="tester")
        )
    approved = engine.apply_approvals(case.case_id, decisions)
    assert approved.status == CaseStatus.APPROVED

    final = engine.execute_approved(case.case_id)
    assert final.status == CaseStatus.COMPLETED
    assert len(final.execution_results) >= 1


def test_rejection_all() -> None:
    engine = CaseWorkflowEngine()
    intake = CaseIntake(request_text="TA Scan data question about oncology landscape and API.")
    case = engine.start_case(intake)
    from src.models.case import ApprovalDecision

    decisions = [
        ApprovalDecision(action_id=a.id, decision="rejected", reviewer="tester")
        for a in case.proposed_actions
    ]
    out = engine.apply_approvals(case.case_id, decisions)
    assert out.status == CaseStatus.REJECTED
    with pytest.raises(ValueError):
        engine.execute_approved(case.case_id)
