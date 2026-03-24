"""RAG context retrieval node (conditional — policy decides when to retrieve)."""

from __future__ import annotations

from config.settings import get_settings
from src.agent.state import GraphState
from src.models.case import CaseStatus, ProductLine
from src.policy.engine import should_retrieve_context


def context_gatherer_node(state: GraphState) -> dict:
    from src.rag.retriever import KnowledgeRetriever

    case = state["case"]
    if not case.classification:
        raise RuntimeError("Classification required before RAG retrieval")

    case.status = CaseStatus.RETRIEVING

    do_retrieve, skip_reason = should_retrieve_context(case)
    if not do_retrieve:
        case.rag_skipped = True
        case.rag_context = []
        case.append_audit("rag_skipped", skip_reason)
        case.status = CaseStatus.ROUTING
        return {"case": case}

    settings = get_settings()
    retriever = KnowledgeRetriever(settings)

    product_hint: str | None = None
    if case.classification.product in (
        ProductLine.TRIALMASTER,
        ProductLine.IRMS_MAX,
        ProductLine.TA_SCAN,
    ):
        product_hint = case.classification.product.value

    query = (
        f"{case.classification.product.value} {case.classification.issue_type.value} "
        f"{case.text_for_llm()[:2000]}"
    )

    try:
        chunks = retriever.retrieve(query, product_hint=product_hint, top_k=6)
    except Exception as exc:
        case.append_audit(
            "rag_retrieval",
            f"RAG retrieval failed; continuing without KB context: {exc}",
            error=str(exc),
        )
        chunks = []

    case.rag_skipped = False
    case.rag_context = chunks
    case.append_audit(
        "rag_retrieval",
        f"Retrieved {len(chunks)} knowledge chunks for routing context.",
        sources=[c.get("metadata", {}).get("source_file") for c in chunks],
    )
    case.status = CaseStatus.ROUTING
    return {"case": case}
