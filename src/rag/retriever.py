"""Retrieve relevant knowledge chunks for agent context."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import Settings, get_settings
from src.rag.vector_store import SqliteVectorStore, list_markdown_files


def _infer_product_tag(source_file: str) -> str:
    name = source_file.lower()
    if "trialmaster" in name:
        return "TrialMaster"
    if "irms" in name:
        return "IRMS MAX"
    if "ta_scan" in name:
        return "TA Scan"
    return "general"


class KnowledgeRetriever:
    """Embedding + vector retrieval with optional product filter."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._store = SqliteVectorStore(self._settings)
        self._embeddings = OpenAIEmbeddings(
            model=self._settings.openai_embedding_model,
            api_key=self._settings.openai_api_key or None,
        )

    @property
    def store(self) -> SqliteVectorStore:
        return self._store

    def embed_query(self, text: str) -> list[float]:
        return self._embeddings.embed_query(text)

    def retrieve(
        self,
        query: str,
        product_hint: str | None = None,
        top_k: int = 6,
    ) -> list[dict[str, Any]]:
        q = self.embed_query(query)
        filt: str | None = None
        if product_hint and product_hint in ("TrialMaster", "IRMS MAX", "TA Scan"):
            filt = product_hint
        try:
            raw = self._store.query(q, n_results=top_k, product_filter=filt)
        except Exception:
            raw = self._store.query(q, n_results=top_k, product_filter=None)
        return raw


def chunk_and_embed_kb(
    settings: Settings,
    kb_dir: Path,
    reset: bool = False,
) -> int:
    """
    Read markdown files, chunk, embed, upsert into SQLite vector store.
    Returns number of chunks stored.
    """
    store = SqliteVectorStore(settings)
    if reset:
        store.clear()

    files = list_markdown_files(kb_dir)
    if not files:
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=120,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key or None,
    )

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []
    all_embeddings: list[list[float]] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        chunks = splitter.split_text(text)
        product = _infer_product_tag(path.name)
        for idx, chunk in enumerate(chunks):
            cid = f"{path.stem}_{idx}"
            ids.append(cid)
            documents.append(chunk)
            metadatas.append(
                {
                    "source_file": path.name,
                    "product": product,
                    "chunk_index": idx,
                }
            )

    if not ids:
        return 0

    all_embeddings = embeddings.embed_documents(documents)
    store.upsert_chunks(ids, documents, metadatas, all_embeddings)
    return len(ids)
