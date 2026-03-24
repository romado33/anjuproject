# TrialMaster — Support and routing

TrialMaster is the electronic data capture (EDC) suite for Phase I–IV clinical trials.

## Common issue categories

- **Export / performance**: Large exports, timeouts, or timeouts when exporting >10k records often route to eClinical Engineering with SLA 24–48h unless audit-critical.
- **Configuration**: Study build, edit checks, and randomization changes require change control; may need validation documentation.
- **Regulatory / audit**: FDA or EU audit preparation requests are escalated to Compliance and Quality; SLA often 8–24h.

## Default routing

- **Primary queue**: `eClinical-Support` — general product issues.
- **Escalation**: `eClinical-Engineering` — performance, defects, or API issues.
- **Professional Services**: Implementation kickoff, migration methodology, or migration cutover.

## Integration notes

- REST APIs are available for integration; issues involving API contracts or connectivity may need Engineering plus a customer-facing integration contact.
