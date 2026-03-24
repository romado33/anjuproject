"""
Deterministic routing when no LLM key is available (CI, local smoke tests).

Keyword classification + **policy engine** for routing/actions (same as online graph).
"""

from __future__ import annotations

import re

from src.models.case import CaseRecord, Classification, IssueType, ProductLine, Urgency
from src.policy.engine import (
    build_actions_from_policy,
    compute_risk_tier,
    rag_influence_note,
    route_from_policy,
)


def _detect_product(text: str) -> ProductLine:
    t = text.lower()
    scores = {
        ProductLine.TRIALMASTER: len(re.findall(r"trialmaster|edc|clinical trial|phase iii|sdtm|cdisc|ctms|trial management|svr|site visit report", t)),
        ProductLine.IRMS_MAX: len(re.findall(r"irms|medical information|crm|veeva|salesforce|therapeutic area|icare|anjubus|msl|medical affairs", t)),
        ProductLine.TA_SCAN: len(re.findall(r"ta scan|competitive|landscape|fda-approved|oncology report|feasibility|kol|investigator identification|site selection|site capacity", t)),
    }
    best = max(scores.items(), key=lambda x: x[1])
    if best[1] == 0:
        if "jira" in t or "ticket" in t:
            return ProductLine.UNKNOWN
        return ProductLine.MULTIPLE if "both" in t or "discrepancy" in t else ProductLine.UNKNOWN
    if sum(1 for v in scores.values() if v == best[1] and v > 0) > 1 and best[1] > 0:
        return ProductLine.MULTIPLE
    return best[0]


def _detect_issue(text: str) -> IssueType:
    t = text.lower()
    if any(x in t for x in ("audit", "fda", "validation doc", "21 cfr", "compliance")):
        return IssueType.COMPLIANCE
    # Implementation before migration: kickoff texts often mention "migration" but are PS programs.
    if any(x in t for x in ("implement", "kickoff", "signed the contract", "onboarding")):
        return IssueType.IMPLEMENTATION
    if any(x in t for x in ("migration", "legacy", "cutover")):
        return IssueType.MIGRATION
    if any(x in t for x in ("training", "learn how", "user guide")):
        return IssueType.TRAINING
    if any(x in t for x in ("timeout", "error", "bug", "failing", "broken")):
        return IssueType.BUG
    if any(x in t for x in ("configure", "configuration", "routing rules", "new therapeutic")):
        return IssueType.CONFIGURATION
    if any(x in t for x in ("report", "data", "api", "export")):
        return IssueType.DATA_QUESTION
    return IssueType.OTHER


def _detect_urgency(text: str) -> Urgency:
    t = text.lower()
    if any(x in t for x in ("outage", "production down", "fda audit next week", "critical")):
        return Urgency.CRITICAL
    if any(x in t for x in ("urgent", "blocked", "asap", "this week")):
        return Urgency.HIGH
    if any(x in t for x in ("when you can", "low priority", "nice to have")):
        return Urgency.LOW
    return Urgency.MEDIUM


def run_offline_pipeline(case: CaseRecord) -> CaseRecord:
    text = case.text_for_llm()
    product = _detect_product(text)
    issue = _detect_issue(text)
    urgency = _detect_urgency(text)

    case.classification = Classification(
        product=product,
        issue_type=issue,
        urgency=urgency,
        sentiment="neutral",
        confidence=0.55,
        reasoning=(
            "Offline mode: keyword heuristics applied (no LLM). "
            "Set OPENAI_API_KEY for full agent reasoning."
        ),
        keywords=[],
    )
    case.append_audit("classification", case.classification.reasoning, mode="offline")

    case.llm_allowed = False
    case.rag_skipped = True
    case.rag_context = []
    case.routing = route_from_policy(case)
    case.append_audit(
        "policy_routing",
        case.routing.reasoning,
        team=case.routing.target_team,
        sla_hours=case.routing.sla_hours,
        mode="offline",
    )
    case.risk_tier = compute_risk_tier(case).value
    case.rag_influence_summary = rag_influence_note(case)
    case.proposed_actions = build_actions_from_policy(case)
    for a in case.proposed_actions:
        case.append_audit(
            "action_proposed",
            f"{a.action_type.value}: {a.title}",
            action_id=a.id,
            mode="offline",
        )
    return case
