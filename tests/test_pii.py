"""PII redaction helpers."""

from __future__ import annotations

from src.utils.pii import redact_pii_text


def test_redact_email() -> None:
    t = "Contact me at user.name+tag@example.com for logs."
    out = redact_pii_text(t)
    assert "@" not in out
    assert "[EMAIL_REDACTED]" in out


def test_redact_preserves_length_category() -> None:
    t = "TrialMaster export issue please advise urgently."
    assert redact_pii_text(t) == t


def test_strict_policy_redacts_trial_tokens() -> None:
    t = "Enrollment issue for NCT12345678 at site #9."
    out = redact_pii_text(t, policy="strict")
    assert "NCT12345678" not in out
    assert "[NCT_REDACTED]" in out
    assert "[SITE_ID_REDACTED]" in out
