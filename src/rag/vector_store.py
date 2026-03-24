"""SQLite-backed vector store (no native compile step; Windows-friendly)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import numpy as np

from config.settings import Settings, get_settings


def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n


def list_markdown_files(kb_dir: Path) -> list[Path]:
    if not kb_dir.exists():
        return []
    return sorted(kb_dir.glob("*.md"))


class SqliteVectorStore:
    """
    Persists chunk embeddings in SQLite.
    Query uses cosine similarity in-process (suitable for internal KB size).
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        path = self._settings.chroma_path()
        path.mkdir(parents=True, exist_ok=True)
        self._db_path = path / "kb_vectors.sqlite3"
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS kb_chunks (
                    id TEXT PRIMARY KEY,
                    document TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )

    def count(self) -> int:
        with self._connect() as c:
            row = c.execute("SELECT COUNT(*) AS n FROM kb_chunks").fetchone()
        return int(row["n"]) if row else 0

    def clear(self) -> None:
        with self._connect() as c:
            c.execute("DELETE FROM kb_chunks")

    def upsert_chunks(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> None:
        if not ids:
            return
        with self._connect() as c:
            for i, cid in enumerate(ids):
                emb = np.asarray(embeddings[i], dtype=np.float32).tobytes()
                meta = json.dumps(metadatas[i], ensure_ascii=False)
                c.execute(
                    """
                    INSERT INTO kb_chunks (id, document, embedding, metadata)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                      document=excluded.document,
                      embedding=excluded.embedding,
                      metadata=excluded.metadata
                    """,
                    (cid, documents[i], emb, meta),
                )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 6,
        product_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        q = _normalize(np.asarray(query_embedding, dtype=np.float32))
        with self._connect() as c:
            rows = c.execute("SELECT id, document, embedding, metadata FROM kb_chunks").fetchall()

        scored: list[tuple[float, dict[str, Any]]] = []
        for row in rows:
            meta = json.loads(row["metadata"])
            if product_filter and meta.get("product") != product_filter:
                continue
            emb = np.frombuffer(row["embedding"], dtype=np.float32)
            sim = float(np.dot(q, _normalize(emb)))
            scored.append(
                (
                    1.0 - sim,
                    {
                        "id": row["id"],
                        "document": row["document"],
                        "metadata": meta,
                        "distance": 1.0 - sim,
                    },
                )
            )
        scored.sort(key=lambda x: x[0])
        return [item[1] for item in scored[:n_results]]
