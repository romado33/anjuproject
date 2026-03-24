"""SQLite persistence for case records (JSON payloads)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.settings import get_settings
from src.models.case import CaseRecord


class CaseStore:
    """Idempotent schema init; thread-safe enough for Streamlit single-user demo."""

    def __init__(self, db_path: Path | None = None) -> None:
        s = get_settings()
        self._path = db_path or s.case_store_full_path()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            c.execute(
                "CREATE INDEX IF NOT EXISTS idx_cases_updated ON cases(updated_at DESC)"
            )

    def upsert(self, record: CaseRecord) -> None:
        payload = record.model_dump(mode="json")
        with self._connect() as c:
            c.execute(
                """
                INSERT INTO cases (case_id, payload, status, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                  payload=excluded.payload,
                  status=excluded.status,
                  updated_at=excluded.updated_at
                """,
                (
                    record.case_id,
                    json.dumps(payload),
                    record.status.value,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def get(self, case_id: str) -> CaseRecord | None:
        with self._connect() as c:
            row = c.execute(
                "SELECT payload FROM cases WHERE case_id = ?", (case_id,)
            ).fetchone()
        if row is None:
            return None
        data: dict[str, Any] = json.loads(row["payload"])
        return CaseRecord.model_validate(data)

    def list_recent(self, limit: int = 50) -> list[CaseRecord]:
        with self._connect() as c:
            rows = c.execute(
                "SELECT payload FROM cases ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        out: list[CaseRecord] = []
        for r in rows:
            data = json.loads(r["payload"])
            out.append(CaseRecord.model_validate(data))
        return out
