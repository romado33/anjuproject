# Internal routing rules — Anju operations

## Divisional structure

Anju operates two divisions, each with a General Manager:
- **eClinical Division** (Tim Lyons): TrialMaster, CTMS Master, Luminee
- **Medical Affairs Division** (Reed McLaughlin): IRMS MAX, iCare MAX, Pubstrat MAX, MA Knowledge
- **Data Science** (TA Scan): Operates across both divisions; has its own brand at ta-scan.io

Routing should align with divisional ownership.

## Team ownership matrix (illustrative)

| Product / domain | Primary team | Escalation |
|------------------|--------------|------------|
| TrialMaster | eClinical-Support | eClinical-Engineering |
| CTMS Master | eClinical-Support | eClinical-Engineering |
| IRMS MAX | MI-Support | MI-Integrations |
| iCare MAX / MA Knowledge | MI-Support | MI-Integrations |
| Pubstrat MAX | MI-Support | MA-Content-Ops |
| TA Scan | TA-Support | TA-DataServices / TA-Platform |
| Cross-product | Program-Management | Executive-Sponsor |

## Urgency

- **Critical**: Production outage, data integrity risk, or regulatory deadline — SLA 4–8h; notify Teams channel `Incident-Ops`.
- **High**: Major workflow blocked — SLA 24h.
- **Medium**: Default — SLA 48–72h.
- **Low**: Best-effort — SLA 5–10 business days.

## Human-in-the-loop

- Any action that creates financial commitments, changes external CRM state, or creates NetSuite project records requires explicit approval in the routing queue.
