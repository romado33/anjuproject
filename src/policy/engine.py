"""
Deterministic policy: AI interprets (classification); policy governs routing and actions.

Operator-grade behavior: selective integrations, not a fixed bundle every time.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any

from src.models.case import (
    ActionType,
    CaseRecord,
    Classification,
    IssueType,
    ProductLine,
    ProposedAction,
    RoutingDecision,
    Urgency,
)


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    RESTRICTED = "restricted"


def compute_risk_tier(case: CaseRecord) -> RiskTier:
    if getattr(case, "restricted_mode", False):
        return RiskTier.RESTRICTED
    c = case.classification
    if not c:
        return RiskTier.MEDIUM
    if c.issue_type == IssueType.COMPLIANCE or c.urgency in (Urgency.HIGH, Urgency.CRITICAL):
        return RiskTier.HIGH
    if c.confidence < 0.55:
        return RiskTier.HIGH
    if c.issue_type == IssueType.DATA_QUESTION and c.urgency == Urgency.LOW:
        return RiskTier.LOW
    return RiskTier.MEDIUM


def should_retrieve_context(case: CaseRecord) -> tuple[bool, str]:
    """
    Conditional RAG: skip when cheap wins; retrieve when ambiguity or compliance demands grounding.
    """
    c = case.classification
    if not c:
        return True, "No classification yet; retrieve for safety."

    if getattr(case, "restricted_mode", False):
        return False, "Restricted case: no retrieval to external embedding API (restricted-content policy)."

    if c.issue_type == IssueType.COMPLIANCE:
        return True, "Compliance/audit: require internal policy and routing KB."

    if c.issue_type in (IssueType.MIGRATION, IssueType.IMPLEMENTATION):
        return True, "Implementation/migration: retrieve playbooks and handoff patterns."

    if c.confidence < 0.65:
        return True, "Low confidence: retrieve to ground routing and reduce mis-triage."

    if c.issue_type == IssueType.BUG and c.urgency in (Urgency.CRITICAL, Urgency.HIGH):
        return True, "High-severity defect: retrieve known issues and escalation paths."

    if c.issue_type == IssueType.DATA_QUESTION and c.product == ProductLine.TA_SCAN:
        return True, "TA Scan data questions: retrieve data-services context."

    # Simple, high-confidence operational paths
    if c.confidence >= 0.75 and c.issue_type in (
        IssueType.TRAINING,
        IssueType.OTHER,
    ):
        return False, "High-confidence training/general: routing matrix sufficient; RAG skipped for latency/cost."

    if c.issue_type == IssueType.DATA_QUESTION and c.confidence >= 0.72 and c.urgency == Urgency.LOW:
        return False, "Simple low-urgency data question: optional KB; skipped in policy tier."

    return True, "Default: retrieve for grounding."


def _kb_text_blob(case: CaseRecord) -> str:
    parts: list[str] = []
    for chunk in case.rag_context or []:
        parts.append(str(chunk.get("document") or chunk.get("text") or ""))
        parts.append(str(chunk.get("metadata") or ""))
    return " ".join(parts).lower()


def _apply_kb_routing_nudges(case: CaseRecord, base: RoutingDecision) -> RoutingDecision:
    """
    When KB chunks contain integration/audit signals, adjust queue or SLA so RAG is visibly outcome-shaping.
    """
    c = case.classification
    if not c or not case.rag_context:
        return base
    blob = _kb_text_blob(case)
    d = base

    if (
        c.product == ProductLine.IRMS_MAX
        and c.issue_type == IssueType.DATA_QUESTION
        and base.target_team == "MI Support"
    ):
        if any(k in blob for k in ("integration", "anjubus", "connector", "veeva")):
            d = base.model_copy(
                update={
                    "target_team": "MI Integrations",
                    "queue_name": "MI-Integrations",
                    "escalation_recommended": True,
                    "reasoning": base.reasoning
                    + (
                        " **RAG influence:** KB snippets reference integration/connector work; "
                        "without retrieval, routing would likely remain on **MI Support** per matrix."
                    ),
                }
            )

    if c.issue_type == IssueType.COMPLIANCE and re.search(
        r"\baudit\b|\bvalidation\b|\b21 cfr\b", blob
    ):
        new_sla = min(d.sla_hours, 12)
        if new_sla < d.sla_hours:
            d = d.model_copy(
                update={
                    "sla_hours": new_sla,
                    "reasoning": d.reasoning
                    + " **RAG influence:** KB reinforced audit/validation language; SLA tightened.",
                }
            )

    return d


def route_from_policy(case: CaseRecord) -> RoutingDecision:
    """Deterministic queue/SLA from classification (no LLM); optional KB nudges when chunks exist."""
    assert case.classification
    c = case.classification
    product, issue, urgency = c.product, c.issue_type, c.urgency

    # Distinct internal paths: compliance vs PS (implementation/migration) vs product support
    if issue == IssueType.COMPLIANCE:
        team, queue = "Quality & Compliance", "QNC-Audit-Review"
    elif issue == IssueType.IMPLEMENTATION:
        team = "Professional Services"
        _impl_q = {
            ProductLine.TRIALMASTER: "PS-eClinical-Onboarding",
            ProductLine.IRMS_MAX: "PS-MI-Onboarding",
            ProductLine.TA_SCAN: "PS-DataServices-Onboarding",
            ProductLine.MULTIPLE: "PS-Cross-Product",
            ProductLine.UNKNOWN: "PS-Intake-Triage",
        }
        queue = _impl_q.get(product, "PS-Implementation")
    elif issue == IssueType.MIGRATION:
        team = "Professional Services"
        queue = "PS-Migration-Cutover"
    elif product == ProductLine.TRIALMASTER:
        team = "eClinical Engineering" if issue == IssueType.BUG else "eClinical Support"
        queue = "TM-General"
    elif product == ProductLine.IRMS_MAX:
        team = "MI Integrations" if issue == IssueType.CONFIGURATION else "MI Support"
        queue = "MI-General"
    elif product == ProductLine.TA_SCAN:
        team = "TA Data Services" if issue == IssueType.DATA_QUESTION else "TA Support"
        queue = "TA-General"
    else:
        team, queue = "Program Management", "Cross-Product"

    prio = "P1" if urgency == Urgency.CRITICAL else "P2" if urgency == Urgency.HIGH else "P3"
    sla = 8 if urgency == Urgency.CRITICAL else 24 if urgency == Urgency.HIGH else 72
    if issue == IssueType.COMPLIANCE:
        sla = min(sla, 24)
    if issue in (IssueType.IMPLEMENTATION, IssueType.MIGRATION):
        sla = min(sla, 120)  # PS programs: allow multi-day window unless critical

    kb_hint = ""
    if case.rag_context:
        kb_hint = (
            f" KB context included {len(case.rag_context)} chunk(s) for traceability; "
            f"queues aligned with internal routing matrix."
        )
    else:
        kb_hint = " No KB retrieval for this path (policy skip); routing from matrix only."

    path_note = ""
    if issue == IssueType.IMPLEMENTATION:
        path_note = (
            " **Path:** Professional Services onboarding — cross-functional work across "
            "delivery, validation, and customer ops (not queue-only support)."
        )
    elif issue == IssueType.MIGRATION:
        path_note = " **Path:** PS migration / cutover — data mapping and go-live coordination."
    elif issue == IssueType.COMPLIANCE:
        path_note = (
            " **Path:** Quality & Compliance — evidence, audit readiness, and sign-off trails."
        )

    base = RoutingDecision(
        target_team=team,
        queue_name=queue,
        priority_label=prio,
        sla_hours=sla,
        escalation_recommended=urgency in (Urgency.CRITICAL, Urgency.HIGH)
        or issue == IssueType.COMPLIANCE,
        reasoning=(
            f"Deterministic policy routing: product={product.value}, issue={issue.value}, "
            f"urgency={urgency.value}.{path_note}{kb_hint}"
        ),
    )
    return _apply_kb_routing_nudges(case, base)


def _simple_ta_data_question(case: CaseRecord) -> bool:
    """Lightweight TA data requests: CRM + Teams only (no Jira noise)."""
    c = case.classification
    if not c:
        return False
    return (
        c.issue_type == IssueType.DATA_QUESTION
        and c.product == ProductLine.TA_SCAN
        and c.urgency == Urgency.LOW
        and c.confidence >= 0.52
    )


def build_actions_from_policy(case: CaseRecord) -> list[ProposedAction]:
    """
    Selective actions — not every case gets Jira + Teams + Salesforce + checklist.
    """
    assert case.classification and case.routing
    c, r = case.classification, case.routing
    actions: list[ProposedAction] = []
    text = case.text_for_llm()

    def jira(reason: str) -> None:
        actions.append(
            ProposedAction(
                action_type=ActionType.JIRA_ISSUE,
                target_system="Jira Cloud",
                title=f"[{c.product.value}] {c.issue_type.value.replace('_', ' ').title()}",
                payload={
                    "project_key": "ANJU",
                    "issue_type": "Task",
                    "summary": f"{c.product.value} — {c.issue_type.value}",
                    "description": text[:4000],
                    "labels": [c.product.value.replace(" ", "-"), c.issue_type.value],
                    "priority": r.priority_label,
                },
                reasoning=reason,
            )
        )

    def teams(reason: str, force: bool = False) -> None:
        if not force and c.urgency not in (Urgency.HIGH, Urgency.CRITICAL):
            if c.issue_type not in (
                IssueType.IMPLEMENTATION,
                IssueType.MIGRATION,
                IssueType.COMPLIANCE,
            ):
                return
        actions.append(
            ProposedAction(
                action_type=ActionType.TEAMS_NOTIFICATION,
                target_system="Microsoft Teams",
                title="Notify owning team channel",
                payload={
                    "channel": "Customer-Ops-Alerts",
                    "message": (
                        f"Case routed to **{r.target_team}** ({r.queue_name}). "
                        f"SLA: {r.sla_hours}h. Urgency: {c.urgency.value}."
                    ),
                    "mention_on_critical": c.urgency == Urgency.CRITICAL,
                },
                reasoning=reason,
            )
        )

    def salesforce(reason: str) -> None:
        actions.append(
            ProposedAction(
                action_type=ActionType.SALESFORCE_ACTIVITY,
                target_system="Salesforce",
                title="Log customer activity on Account",
                payload={
                    "object": "Task",
                    "subject": f"Inbound: {c.issue_type.value}",
                    "description_snippet": text[:2000],
                    "related_product__c": c.product.value,
                },
                reasoning=reason,
            )
        )

    # --- Policy matrix ---
    simple_ta = _simple_ta_data_question(case)

    if simple_ta:
        salesforce(
            "Policy: lightweight TA Scan data question — CRM trail only (no Jira noise)."
        )
        teams(
            "Policy: notify TA Data Services channel for scoping (no Jira for this tier).",
            force=True,
        )
        return actions

    if c.issue_type == IssueType.COMPLIANCE:
        jira("Compliance/audit: mandatory tracked work item.")
        teams("Compliance: executive visibility required.", force=True)
        salesforce("Compliance: CRM activity record for account governance.")
        actions.append(
            ProposedAction(
                action_type=ActionType.IMPLEMENTATION_CHECKLIST,
                target_system="Internal Wiki / Confluence",
                title="Audit readiness checklist",
                payload={
                    "sections": [
                        "Validation evidence index",
                        "Sign-off trail",
                        "Change records",
                    ]
                },
                reasoning="Compliance: structured audit artifacts; restricted gate may block external LLM.",
            )
        )
        return actions

    if c.issue_type == IssueType.IMPLEMENTATION:
        actions.append(
            ProposedAction(
                action_type=ActionType.JIRA_ISSUE,
                target_system="Jira Cloud",
                title=f"PS program: [{c.product.value}] implementation / onboarding",
                payload={
                    "project_key": "ANJU",
                    "issue_type": "Epic",
                    "summary": f"Onboarding — {c.product.value}",
                    "description": text[:4000],
                    "labels": ["professional-services", c.product.value.replace(" ", "-")],
                    "priority": r.priority_label,
                },
                reasoning="Policy: PS-owned epic for cross-functional onboarding (delivery, validation, training).",
            )
        )
        teams(
            "Policy: PS pod + customer success coordination (implementation is not queue-only support).",
            force=True,
        )
        salesforce(
            "Policy: CRM milestone for SOW stage, stakeholders, and account governance."
        )
        actions.append(
            ProposedAction(
                action_type=ActionType.NETSUITE_TIME_OR_PROJECT,
                target_system="NetSuite",
                title="PS project / billing alignment",
                payload={
                    "project_code": "PS-IMPLEMENTATION",
                    "note": "Confirm SOW line items, billing code, and milestone dates with Finance.",
                },
                reasoning="Policy: finance/PS touchpoint for scoped implementation work.",
            )
        )
        actions.append(
            ProposedAction(
                action_type=ActionType.BAMBOOHR_TASK,
                target_system="BambooHR",
                title="Staffing / onboarding checklist (if pod changes)",
                payload={
                    "task_template": "implementation_pod_onboarding",
                    "assignee_role": "PS_Manager",
                },
                reasoning="Policy: HR only when staffing motion is implied.",
            )
        )
        actions.append(
            ProposedAction(
                action_type=ActionType.IMPLEMENTATION_CHECKLIST,
                target_system="Internal Wiki / Confluence",
                title="Implementation playbook",
                payload={
                    "sections": [
                        "Discovery & success criteria",
                        "Integration endpoints (AnjuBUS)",
                        "Validation plan",
                        "Training cutover",
                        "Migration risks",
                    ]
                },
                reasoning="Policy: structured PS artifacts — distinct from ad-hoc support tickets.",
            )
        )
        return actions

    if c.issue_type == IssueType.MIGRATION:
        jira(
            "Policy: traceable migration work item (cutover, mapping, rollback) under PS."
        )
        teams("Policy: migration coordination across PS, Support, and customer.", force=True)
        salesforce("Policy: CRM note for migration window and stakeholder comms.")
        actions.append(
            ProposedAction(
                action_type=ActionType.NETSUITE_TIME_OR_PROJECT,
                target_system="NetSuite",
                title="PS / services billing checkpoint",
                payload={
                    "project_code": "PS-MIGRATION",
                    "note": "Scoped migration — confirm SOW hours and cutover billing.",
                },
                reasoning="Policy: PS/finance checkpoint for migration programs.",
            )
        )
        actions.append(
            ProposedAction(
                action_type=ActionType.IMPLEMENTATION_CHECKLIST,
                target_system="Internal Wiki / Confluence",
                title="Migration runbook",
                payload={
                    "sections": ["Data mapping", "Cutover plan", "Rollback", "Validation sign-off"]
                },
                reasoning="Policy: migration-specific artifacts (distinct from implementation kickoff).",
            )
        )
        return actions

    # Default path: Jira for traceability
    jira("Policy: traceable work item for Support/Engineering triage.")

    if c.issue_type == IssueType.BUG:
        teams(
            "Policy: Teams for defects only when severity warrants broadcast.",
            force=c.urgency in (Urgency.HIGH, Urgency.CRITICAL),
        )
    elif c.issue_type in (
        IssueType.CONFIGURATION,
        IssueType.TRAINING,
        IssueType.OTHER,
    ):
        teams("Policy: coordination channel for non-defect work.", force=True)

    if c.issue_type not in (IssueType.BUG,) or c.urgency in (
        Urgency.MEDIUM,
        Urgency.HIGH,
        Urgency.CRITICAL,
    ):
        if not (c.issue_type == IssueType.BUG and c.urgency == Urgency.LOW):
            salesforce(
                "Policy: preserve commercial/account context when acting across systems."
            )

    return actions


def rag_influence_note(case: CaseRecord) -> str | None:
    """Explain whether KB retrieval plausibly affected routing (for UI)."""
    if getattr(case, "restricted_mode", False):
        return (
            "Restricted case: no KB retrieval to external embedding API. "
            "Routing and actions are deterministic only."
        )
    if getattr(case, "rag_skipped", None):
        return (
            "RAG was skipped by policy (latency/cost tier). "
            "Routing used deterministic matrix only — check audit for `rag_skipped`."
        )
    if not case.rag_context:
        return None
    extra = ""
    if case.routing and "RAG influence" in (case.routing.reasoning or ""):
        extra = " See routing reasoning for a concrete **RAG influence** line (queue/SLA nudge)."
    return (
        f"Retrieval added {len(case.rag_context)} chunk(s) from internal KB.{extra} "
        f"Open the routing step to compare baseline matrix vs KB-informed outcome."
    )


def approval_elevated(case: CaseRecord) -> bool:
    """Whether this case should be called out for stricter human review (heuristic)."""
    t = compute_risk_tier(case)
    c = case.classification
    return (
        t in (RiskTier.HIGH, RiskTier.RESTRICTED)
        or (c is not None and c.issue_type == IssueType.COMPLIANCE)
    )


def policy_controls_snapshot(case: CaseRecord) -> dict[str, Any]:
    """Structured view for Policy & Controls UI."""
    tier = compute_risk_tier(case)
    notes: list[str] = []
    if tier == RiskTier.RESTRICTED:
        notes.append("External LLM calls blocked; embeddings not used for retrieval.")
    if case.rag_skipped:
        notes.append("KB retrieval skipped — see `rag_skipped` audit entry.")
    if case.classification and _simple_ta_data_question(case):
        notes.append("Selective path: Jira omitted for lightweight TA Scan data requests.")
    if case.classification and case.classification.issue_type == IssueType.COMPLIANCE:
        notes.append("Compliance: mandatory tracked items + executive visibility per policy matrix.")
    if case.classification and case.classification.issue_type == IssueType.IMPLEMENTATION:
        notes.append("PS path: onboarding / implementation — epic + checklists + finance touchpoints.")
    if case.classification and case.classification.issue_type == IssueType.MIGRATION:
        notes.append("PS migration path: cutover/mapping runbook — distinct from day-to-day support.")

    return {
        "risk_tier": tier.value,
        "llm_allowed": case.llm_allowed,
        "restricted_mode": case.restricted_mode,
        "restricted_signals": list(case.restricted_signals),
        "rag_skipped": case.rag_skipped,
        "human_approval_gate": True,
        "elevated_human_review": approval_elevated(case),
        "proposed_action_types": [a.action_type.value for a in case.proposed_actions],
        "policy_notes": notes,
        "rag_influence_summary": case.rag_influence_summary,
    }


def aggregate_operator_metrics(cases: list[CaseRecord]) -> dict[str, Any]:
    """
    Aggregate metrics for Case run dashboard — business-style signals, not only pipeline state.

    Handoffs-reduced uses an illustrative pre-automation systems-touch count vs mean proposed actions.
    """
    n = len(cases)
    if n == 0:
        return {
            "handoffs_reduced_est": 0.0,
            "cases_without_external_llm": 0,
            "cases_no_jira_ticket": 0,
            "cases_elevated_review": 0,
        }

    systems_before = 4.2
    action_counts = [len(c.proposed_actions or []) for c in cases]
    avg_actions = sum(action_counts) / n
    handoffs_reduced = max(0.0, systems_before - avg_actions)

    without_llm = sum(1 for c in cases if not c.llm_allowed)
    no_jira = sum(
        1
        for c in cases
        if c.proposed_actions
        and not any(a.action_type == ActionType.JIRA_ISSUE for a in c.proposed_actions)
    )
    elevated = sum(1 for c in cases if approval_elevated(c))

    return {
        "handoffs_reduced_est": round(handoffs_reduced, 1),
        "cases_without_external_llm": without_llm,
        "cases_no_jira_ticket": no_jira,
        "cases_elevated_review": elevated,
    }
