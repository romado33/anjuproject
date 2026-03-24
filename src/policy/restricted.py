"""
Heuristic detection of content that should not use external LLMs (demo).

Production would use DLP, classifiers, and legal policy — not regex alone.
"""

from __future__ import annotations

import re
from typing import NamedTuple


class RestrictedAnalysis(NamedTuple):
    is_restricted: bool
    signals: list[str]
    block_external_llm: bool


# High-risk phrases (case-insensitive)
_SENSITIVE_PATTERNS: list[tuple[str, str]] = [
    (r"\bMRN\b", "possible_medical_record_number"),
    (r"\bpatient\s+id\b", "patient_identifier_language"),
    (r"\bsubject\s+id\b", "subject_identifier_language"),
    (r"\badverse\s+event\b", "adverse_event_language"),
    (r"\bAE\s+report\b", "adverse_event_report"),
    (r"\bSAE\b", "serious_adverse_event"),
    (r"\bphi\b", "phi_mention"),
    (r"\bprotected\s+health\s+information\b", "phi_mention"),
    (r"\bdate\s+of\s+birth\b", "dob_mention"),
    (r"\bdiagnosis\b.*\bpatient\b", "clinical_diagnosis_context"),
    (r"\bprotocol\s*#\s*\d+", "protocol_number_pattern"),
    (r"\bNCT\d{8}\b", "clinicaltrials_gov_id"),
]


def analyze_restricted(text: str) -> RestrictedAnalysis:
    """If any pattern matches, block external LLM path for this case (demo policy)."""
    t = text.lower()
    signals: list[str] = []
    for pattern, label in _SENSITIVE_PATTERNS:
        if re.search(pattern, t, re.IGNORECASE):
            signals.append(label)
    # Short free-text names are hard; flag obvious study-site combo
    if re.search(r"\bsite\s*#?\s*\d+", t, re.IGNORECASE):
        signals.append("site_identifier_language")

    is_restricted = len(signals) > 0
    return RestrictedAnalysis(
        is_restricted=is_restricted,
        signals=signals,
        block_external_llm=is_restricted,
    )
