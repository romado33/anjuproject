#!/usr/bin/env python3
"""
Seed the SQLite vector store from data/knowledge_base/*.md files.

Usage (from project root):
  $env:PYTHONPATH="."
  python scripts/seed_knowledge_base.py [--reset]

Requires OPENAI_API_KEY for embedding generation.
Idempotent: skips if the store already has documents unless --reset.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.logging_config import configure_logging, get_logger
from config.settings import get_settings
from src.rag.retriever import chunk_and_embed_kb
from src.rag.vector_store import SqliteVectorStore


def main() -> int:
    configure_logging()
    log = get_logger("seed_kb")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate the Chroma collection before seeding",
    )
    args = parser.parse_args()

    settings = get_settings()
    if settings.use_offline_mode():
        log.warning(
            "event=seed_skipped",
            reason="offline_mode_no_openai_key",
            detail="Embeddings require OPENAI_API_KEY. Offline mode can run without RAG.",
        )
        return 0

    kb_dir = ROOT / "data" / "knowledge_base"
    store = SqliteVectorStore(settings)
    if not args.reset and store.count() > 0:
        log.info("event=seed_skipped", reason="collection_nonempty", count=store.count())
        return 0

    n = chunk_and_embed_kb(settings, kb_dir, reset=args.reset)
    log.info("event=seed_complete", chunks=n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
