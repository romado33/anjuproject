"""Redaction integrated with offline pipeline."""

from __future__ import annotations

import os

os.environ["OFFLINE_DEMO"] = "true"
os.environ["OPENAI_API_KEY"] = ""

from src.models.case import CaseIntake
from src.workflow.engine import CaseWorkflowEngine


def test_redaction_applied_before_processing() -> None:
    engine = CaseWorkflowEngine()
    intake = CaseIntake(
        request_text=(
            "TrialMaster issue: export fails. Escalate to lead@customer.org "
            "or call 514-555-0199 urgently."
        ),
        redact_pii=True,
    )
    case = engine.start_case(intake)
    assert case.redacted_request_text is not None
    assert "[EMAIL_REDACTED]" in case.redacted_request_text
    assert "lead@" not in case.redacted_request_text
    assert any(step.step == "pii_redaction" for step in case.audit_trail)
