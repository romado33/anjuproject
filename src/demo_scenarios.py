"""Pre-built demo scenarios for interviews and UI shortcuts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoScenario:
    key: str
    title: str
    description: str
    request_text: str


SCENARIOS: list[DemoScenario] = [
    DemoScenario(
        key="impl_kickoff",
        title="Implementation kickoff — IRMS MAX",
        description="PS onboarding: routing, actions, checklist (recommended first in interview)",
        request_text=(
            "We signed the contract for IRMS MAX last Friday. We need to kick off "
            "implementation including migration from our legacy MI system, validation "
            "documentation, and training for our medical information team."
        ),
    ),
    DemoScenario(
        key="compliance_audit",
        title="Compliance — FDA audit prep",
        description="Q&C path + restricted-style narrative (recommended second)",
        request_text=(
            "We have an FDA inspection next week. We need validation evidence for "
            "TrialMaster configuration changes made in the last quarter, including "
            "audit trails and sign-off records."
        ),
    ),
    DemoScenario(
        key="tm_export",
        title="TrialMaster — large export timeout",
        description="EDC performance / engineering escalation pattern",
        request_text=(
            "We are running a Phase III study in TrialMaster. When we export more than "
            "10,000 records the job times out after 30 minutes. This is blocking our "
            "SDTM deliverable for next week. Please advise urgently."
        ),
    ),
    DemoScenario(
        key="irms_crm",
        title="IRMS MAX — CRM routing configuration",
        description="Medical information + CRM integration",
        request_text=(
            "We need to add a new therapeutic area in IRMS MAX and update the medical "
            "inquiry routing rules so requests route to the correct MSL pod. We use "
            "Salesforce as our CRM and need activities mirrored for compliance."
        ),
    ),
    DemoScenario(
        key="ta_scan",
        title="TA Scan — custom competitive report",
        description="Data services scoping + delivery",
        request_text=(
            "Can TA Scan provide a custom competitive landscape for FDA-approved oncology "
            "therapies in the US and EU from the last 18 months, delivered via API weekly? "
            "Please scope effort and timeline."
        ),
    ),
    DemoScenario(
        key="cross_product",
        title="Cross-product discrepancy",
        description="Program management + multiple product lines",
        request_text=(
            "We are seeing discrepancies between TrialMaster enrollment counts and what "
            "TA Scan shows for the same investigational product. Can someone help reconcile "
            "definitions and identify whether this is a data issue or mapping issue?"
        ),
    ),
]


def get_scenario(key: str) -> DemoScenario | None:
    for s in SCENARIOS:
        if s.key == key:
            return s
    return None
