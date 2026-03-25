# AnjuBUS integration platform (conceptual)

AnjuBUS is the integration layer for real-time and batch connectivity between Anju products and external systems. It is built on the Anju Technology platform.

## Technology platform capabilities

- **Secured global repository**: Single source of truth across SQL and No-SQL data stores.
- **Streamlined workflows**: Pre-configured or custom workflows for cross-departmental collaboration.
- **Natural language queries**: English-like guided searches for building reports and dashboards.
- **Dashboard designer**: Built-in analytics, visuals, layouts, and filters.
- **Office 365 integration**: Document editing with audit trail.
- **Mobile applications**: Agnostic mobile app support for clinical and medical affairs use cases.

## Adapter pattern

- Pre-built adapters available for CRM apps: **Salesforce**, **Veeva**, **MS CRM**, and other standard applications.
- Adapters provide **unidirectional or bi-directional** flow of data.
- Supports **real-time and batch processing** use cases at scale.
- In production, an orchestration layer invokes adapters with validated payloads and captures responses for audit.
- Additional adapters registered for: Jira, Teams, NetSuite, BambooHR, HR systems, internal wiki/Confluence.

## Integration with Anju products

- **IRMS MAX**: CRM sync (Salesforce, Veeva), AE/PC transfer to safety systems, content management.
- **TrialMaster**: EDC data exports, SAS dataset generation, third-party system integration via REST APIs.
- **CTMS Master**: Integration with TrialMaster and other EDCs, eTMF document mapping.
- **TA Scan**: API services for data delivery into customer CTMS/CRM/data lakes.

## AI routing layer (this application)

- An **AI routing layer** classifies unstructured customer requests, retrieves relevant product/process context, and proposes adapter invocations.
- Human approval gates precede writes to systems of record.
- This pattern sits **above** the adapter layer — orchestrating and governing automation, not replacing existing integration infrastructure.
