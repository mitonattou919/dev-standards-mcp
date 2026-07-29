"""sample-knowledge(またはGitHub正本)からパースしたドキュメントをSQLiteへ投入する。

SQLiteは再生成可能な検索インデックスであるため、ビルドの都度スキーマごと作り直す。
"""

import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path

from src.domain.document import OkfDocument
from src.parser.okf_parser import parse_directory
from src.repository.schema import (
    CREATE_DOCUMENTS_TABLE,
    CREATE_FTS_TABLE,
    DROP_DOCUMENTS_TABLE,
    DROP_FTS_TABLE,
    INSERT_DOCUMENT,
    REBUILD_FTS_INDEX,
)


def build_index(conn: sqlite3.Connection, documents: Iterable[OkfDocument]) -> None:
    conn.execute(DROP_FTS_TABLE)
    conn.execute(DROP_DOCUMENTS_TABLE)
    conn.execute(CREATE_DOCUMENTS_TABLE)
    conn.execute(CREATE_FTS_TABLE)

    conn.executemany(INSERT_DOCUMENT, [_to_row(document) for document in documents])

    conn.execute(REBUILD_FTS_INDEX)
    conn.commit()


def build_index_from_directory(conn: sqlite3.Connection, directory: Path) -> None:
    build_index(conn, parse_directory(directory))


def _to_row(document: OkfDocument) -> dict[str, object]:
    return {
        "id": document.id,
        "type": document.type,
        "title": document.title,
        "summary": document.summary,
        "status": document.status,
        "owner": document.owner,
        "tags": json.dumps(document.tags),
        "body": document.body,
        "rule_level": document.rule_level,
        "technologies": json.dumps(document.technologies) if document.technologies is not None else None,
        "applies_to": json.dumps(document.applies_to) if document.applies_to is not None else None,
        "version": document.version,
        "effective_date": document.effective_date.isoformat() if document.effective_date else None,
    }
