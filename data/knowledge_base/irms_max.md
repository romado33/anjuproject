# IRMS MAX — Medical information and CRM integration

IRMS MAX is the gold standard medical information system for life sciences. It manages medical inquiry workflows, adverse event and product complaint intake, and integrates with CRM environments.

## Key capabilities

- **Multi-channel case intake**: Email, fax, web, CTI (computer telephony integration) — centralized entry point for all medical information requests.
- **AE and product complaint modules**: Centralized intake with seamless transfer and tracking to safety and product quality systems.
- **CRM integration**: Pre-built adapters for Salesforce, Veeva, MS CRM via the Anju Technology platform. Bi-directional, real-time or batch data flow.
- **Quality assurance module**: Business rules for flagging cases for review; reviewer dashboards.
- **Compliance**: GDPR, 21 CFR Part 11, role-based access, audit trails, privacy controls, detailed case logs.
- **Analytics**: Built-in reporting engine with visual dashboards, self-service natural language queries, out-of-the-box metrics and trending reports.
- **Global deployments**: Division feature supports local/regional/global scale with configuration (not customization), data segregation, and multi-lingual support.
- **Cloud or on-premise**: Azure cloud-hosted or on-premise deployment options.

## Related Medical Affairs products

- **iCare MAX**: Self-service portal for HCPs/consumers. Fully integrated with IRMS MAX content. HCP self-attestation, Azure-hosted.
- **Pubstrat MAX**: Publication planning — online collaboration, JSCA database for journal/conference targeting.
- **MA Knowledge**: Content delivery for MSLs and field reps — smart filtering, dynamic workspace, pulls from IRMS MAX and external links.

## Common issue categories

- **CRM sync**: Contact matching, account hierarchy, activity feed issues, or duplicate records — route to `MI-Integrations` with SLA 24–72h.
- **Configuration**: Therapeutic areas, medical inquiry routing rules, division setup, QA module rules — often `MI-Support` with possible PS involvement.
- **Compliance**: Adverse event handling, audit trails, regulatory correspondence, 21 CFR Part 11 questions — escalate to `MI-Compliance`.
- **Content / portal**: iCare MAX content publishing, MA Knowledge access, or Pubstrat MAX workflow issues — `MI-Support` initially.

## Default routing

- **Primary queue**: `MI-Support` — general product issues.
- **Escalation**: `MI-Integrations` — CRM or AnjuBUS adapter connectivity (Salesforce, Veeva, MS CRM).
- **Professional Services**: Implementation, migration, training, validation documentation.

## Integration notes

- AnjuBUS provides pre-built adapters for CRM and batch/real-time flows. Issues may require adapter logs and endpoint configuration review.
- IRMS MAX integrates with safety systems for AE/PC transfer — tracking of acknowledgements back to ensure receipt.
