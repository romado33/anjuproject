# Privacy, audit, and internal handling (reference)

## Principles for internal automation

- **Data minimization:** send only the text required for triage to external models when policy allows.
- **Audit trail:** record classification, routing, and human approvals for operational and compliance review.
- **Human-in-the-loop:** material writes to systems of record (Jira, CRM, finance) should be approved by authorized staff.
- **Regional nuance:** United States (HIPAA/PHI for covered data) and Canada (PIPEDA / provincial health privacy) differ; Legal defines scope.

## Support and implementation context

- Customer-submitted text may contain sensitive information; treat inbound channels as **restricted** and log access appropriately.
