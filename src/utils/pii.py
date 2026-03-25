"""
Best-effort PII / sensitive-data redaction for defense-in-depth before LLM calls.

Not a HIPAA compliance tool — production systems need DLP, classification,
legal review, and jurisdiction-specific controls.

Redaction policies are configurable via the `policy` argument.
"""

from __future__ import annotations

import re
from typing import Literal

_EMAIL = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)
# US-style phone; loose match for intake text
_PHONE = re.compile(
    r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b",
)
_NCT = re.compile(r"\bNCT\d{8}\b", re.IGNORECASE)
_SITE_ID = re.compile(r"\bsite\s*#?\s*\d+\b", re.IGNORECASE)
# Common study / protocol style tokens (high false-positive risk; use only in "strict")
_STUDY_LIKE = re.compile(r"\b(?:study|protocol)\s*#?\s*[A-Z0-9]{4,}\b", re.IGNORECASE)

RedactionPolicy = Literal["standard", "strict"]


def redact_pii_text(text: str, *, policy: RedactionPolicy = "standard") -> str:
    """
    Mask common direct identifiers and (in strict mode) additional study/protocol tokens.

    Strict mode also covers study IDs, trial registry IDs, and site identifiers — not as a
    replacement for enterprise DLP.
    """
    out = _EMAIL.sub("[EMAIL_REDACTED]", text)
    out = _PHONE.sub("[PHONE_REDACTED]", out)
    if policy == "strict":
        out = _NCT.sub("[NCT_REDACTED]", out)
        out = _SITE_ID.sub("[SITE_ID_REDACTED]", out)
        out = _STUDY_LIKE.sub("[STUDY_TOKEN_REDACTED]", out)
    return out
