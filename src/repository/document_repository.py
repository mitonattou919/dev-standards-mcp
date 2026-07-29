"""ドキュメントのRepository層。ToolやServiceはSQLiteへ直接アクセスせず、必ずこの層を経由する。"""

import json
import sqlite3
from datetime import date
from typing import Protocol

from src.domain.document import OkfDocument


class DocumentRepository(Protocol):
    def get(self, document_id: str) -> OkfDocument | None: ...

    def list_by_metadata(
        self,
        *,
        type: str | None = None,
        technology: str | None = None,
        rule_level: str | None = None,
        status: str | None = None,
        applies_to: str | None = None,
    ) -> list[OkfDocument]: ...


class SqliteDocumentRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        conn.row_factory = sqlite3.Row
        self._conn = conn

    def get(self, document_id: str) -> OkfDocument | None:
        cursor = self._conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
        row = cursor.fetchone()
        return _row_to_document(row) if row is not None else None

    def list_by_metadata(
        self,
        *,
        type: str | None = None,
        technology: str | None = None,
        rule_level: str | None = None,
        status: str | None = None,
        applies_to: str | None = None,
    ) -> list[OkfDocument]:
        clauses: list[str] = []
        params: list[str] = []

        if type is not None:
            clauses.append("documents.type = ?")
            params.append(type)
        if rule_level is not None:
            clauses.append("documents.rule_level = ?")
            params.append(rule_level)
        if status is not None:
            clauses.append("documents.status = ?")
            params.append(status)
        if technology is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM json_each(documents.technologies) WHERE json_each.value = ?)"
            )
            params.append(technology)
        if applies_to is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM json_each(documents.applies_to) WHERE json_each.value = ?)"
            )
            params.append(applies_to)

        sql = "SELECT * FROM documents"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY id"

        cursor = self._conn.execute(sql, params)
        return [_row_to_document(row) for row in cursor.fetchall()]


def _row_to_document(row: sqlite3.Row) -> OkfDocument:
    return OkfDocument(
        type=row["type"],
        id=row["id"],
        title=row["title"],
        summary=row["summary"],
        status=row["status"],
        owner=row["owner"],
        tags=json.loads(row["tags"]),
        body=row["body"],
        rule_level=row["rule_level"],
        technologies=json.loads(row["technologies"]) if row["technologies"] is not None else None,
        applies_to=json.loads(row["applies_to"]) if row["applies_to"] is not None else None,
        version=row["version"],
        effective_date=date.fromisoformat(row["effective_date"]) if row["effective_date"] else None,
    )
