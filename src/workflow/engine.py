"""Orchestrate pipeline runs, approvals, and adapter execution."""

from __future__ import annotations

from src.agent.orchestrator import run_agent_pipeline
from src.integrations.registry import get_default_registry
from src.models.case import (
    ApprovalDecision,
    CaseIntake,
    CaseRecord,
    CaseStatus,
    ProposedAction,
)
from src.utils.pii import redact_pii_text
from src.workflow.store import CaseStore


class CaseWorkflowEngine:
    """High-level API used by Streamlit."""

    def __init__(self, store: CaseStore | None = None) -> None:
        self._store = store or CaseStore()
        self._registry = get_default_registry()

    def start_case(self, intake: CaseIntake) -> CaseRecord:
        case = CaseRecord(intake=intake, status=CaseStatus.INTAKE)
        if intake.redact_pii:
            case.redacted_request_text = redact_pii_text(
                intake.request_text,
                policy=intake.redaction_policy,
            )
            case.append_audit(
                "pii_redaction",
                "Demo: emails/phone-like tokens masked before LLM/embeddings. "
                "Original request remains in intake for authorized review.",
                redacted=True,
            )
        case = run_agent_pipeline(case)
        self._store.upsert(case)
        return case

    def get_case(self, case_id: str) -> CaseRecord | None:
        return self._store.get(case_id)

    def list_cases(self, limit: int = 50) -> list[CaseRecord]:
        return self._store.list_recent(limit=limit)

    def apply_approvals(
        self,
        case_id: str,
        decisions: list[ApprovalDecision],
    ) -> CaseRecord:
        case = self._store.get(case_id)
        if case is None:
            raise KeyError(f"Unknown case_id={case_id}")
        case.approvals.extend(decisions)
        for d in decisions:
            case.append_audit(
                "human_approval",
                f"Decision={d.decision} for action {d.action_id}",
                reviewer=d.reviewer,
            )

        if decisions and all(d.decision == "rejected" for d in decisions):
            case.status = CaseStatus.REJECTED
        else:
            case.status = CaseStatus.APPROVED

        self._store.upsert(case)
        return case

    def execute_approved(self, case_id: str) -> CaseRecord:
        """Run mock adapters for approved or modified actions."""
        case = self._store.get(case_id)
        if case is None:
            raise KeyError(f"Unknown case_id={case_id}")
        if case.status == CaseStatus.REJECTED:
            raise ValueError("Case rejected; nothing to execute.")
        if case.status != CaseStatus.APPROVED:
            raise ValueError(
                "Submit and record approval decisions before execution. "
                f"Current status: {case.status.value}"
            )

        approvals_by_id = {a.action_id: a for a in case.approvals}
        if not approvals_by_id:
            raise ValueError("No approval decisions recorded for this case.")

        case.status = CaseStatus.EXECUTING
        self._store.upsert(case)

        for action in case.proposed_actions:
            dec = approvals_by_id.get(action.id)
            if dec is None:
                continue
            if dec.decision == "rejected":
                continue

            exec_action: ProposedAction = action
            if dec.decision == "modified" and dec.modified_payload is not None:
                exec_action = action.model_copy(update={"payload": dec.modified_payload})

            res = self._registry.dispatch(exec_action, case.case_id)
            case.execution_results.append({"action_id": action.id, "result": res})
            case.append_audit(
                "adapter_execution",
                f"Executed {exec_action.action_type.value} on {exec_action.target_system}",
                action_id=action.id,
                result=res,
            )

        case.status = CaseStatus.COMPLETED
        self._store.upsert(case)
        return case
