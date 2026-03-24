"""Classification agent node."""

from __future__ import annotations

from config.settings import Settings, get_settings
from src.agent.llm import get_openai_client
from src.agent.state import GraphState
from src.models.case import CaseStatus, Classification


_CLASSIFIER_INSTRUCTIONS = """You are the internal triage classifier for Anju Software (life sciences).
Classify the customer/internal request into:
- product: one of TrialMaster, IRMS MAX, TA Scan, Multiple / Cross-product, Unknown
- issue_type: bug, configuration_request, training, migration, data_question, implementation, compliance, other
- urgency: critical, high, medium, low
- sentiment: short label (e.g., frustrated, neutral, calm)
- confidence: 0-1 how confident you are
- reasoning: 3-6 sentences citing signals from the text (no PII beyond what user provided)
- keywords: up to 12 salient tokens
Be conservative: if unclear, lower confidence and choose Unknown/other appropriately.
"""


def classify_node(state: GraphState, settings: Settings | None = None) -> dict:
    s = settings or get_settings()
    case = state["case"]
    case.status = CaseStatus.CLASSIFYING

    client = get_openai_client(s)
    completion = client.beta.chat.completions.parse(
        model=s.openai_chat_model,
        messages=[
            {"role": "system", "content": _CLASSIFIER_INSTRUCTIONS},
            {
                "role": "user",
                "content": (
                    f"Source channel: {case.intake.source_channel}\n\n"
                    f"Request:\n{case.text_for_llm()}"
                ),
            },
        ],
        response_format=Classification,
        temperature=0.2,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("Classification model returned empty parsed content")
    case.classification = parsed
    case.append_audit(
        "classification",
        parsed.reasoning,
        confidence=parsed.confidence,
        product=parsed.product.value,
    )
    case.llm_allowed = True
    return {"case": case}
