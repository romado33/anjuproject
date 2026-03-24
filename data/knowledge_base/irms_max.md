# IRMS MAX — Medical information and CRM integration

IRMS MAX manages medical information workflows and integrates with CRM environments (e.g., Salesforce, Veeva).

## Common issue categories

- **CRM sync**: Contact matching, account hierarchy, activity feed issues, or duplicate records — often route to `MI-Integrations` with SLA 24–72h.
- **Configuration**: Therapeutic areas, medical inquiry routing rules, or division setup — often `MI-Support` with possible PS involvement.
- **Compliance**: Adverse event handling, audit trails, or regulatory correspondence — escalate to `MI-Compliance`.

## Default routing

- **Primary queue**: `MI-Support` — general product issues.
- **Escalation**: `MI-Integrations` — CRM or AnjuBUS adapter connectivity.
- **Professional Services**: Implementation, migration, training, or validation documentation.

## Integration notes

- AnjuBUS provides pre-built adapters for CRM and batch/real-time flows. Issues may require adapter logs and endpoint configuration review.
