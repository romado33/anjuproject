# AnjuBUS integration platform (conceptual)

AnjuBUS is the integration layer for real-time and batch connectivity between Anju products and external systems.

## Adapter pattern

- Adapters are registered for endpoints such as Salesforce, Veeva, Microsoft CRM, Jira, Teams, and HR systems.
- In production, an orchestration layer invokes adapters with validated payloads and captures responses for audit.

## AI routing layer (demo concept)

- An **AI routing layer** classifies unstructured customer requests, retrieves relevant product/process context, and proposes adapter invocations.
- Human approval gates precede writes to systems of record.
