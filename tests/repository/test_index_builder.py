import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from src.domain.document import OkfDocument
from src.repository.index_builder import build_index, build_index_from_directory


@pytest.fixture
def empty_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_build_index_inserts_documents(
    empty_conn: sqlite3.Connection, sample_documents: list[OkfDocument]
) -> None:
    build_index(empty_conn, sample_documents)

    rows = empty_conn.execute("SELECT id FROM documents ORDER BY id").fetchall()
    assert [row[0] for row in rows] == [
        "guideline-review",
        "standard-python-naming",
        "standard-typescript-strict",
    ]


def test_build_index_populates_fts_table(
    empty_conn: sqlite3.Connection, sample_documents: list[OkfDocument]
) -> None:
    build_index(empty_conn, sample_documents)

    count = empty_conn.execute("SELECT count(*) FROM documents_fts").fetchone()[0]
    assert count == len(sample_documents)


def test_build_index_is_rebuildable(
    empty_conn: sqlite3.Connection, sample_documents: list[OkfDocument]
) -> None:
    build_index(empty_conn, sample_documents)
    build_index(empty_conn, sample_documents[:1])

    rows = empty_conn.execute("SELECT id FROM documents").fetchall()
    assert [row[0] for row in rows] == ["standard-python-naming"]


def test_build_index_from_directory_uses_parser(empty_conn: sqlite3.Connection) -> None:
    sample_knowledge = Path(__file__).parent.parent.parent / "sample-knowledge"

    build_index_from_directory(empty_conn, sample_knowledge)

    rows = empty_conn.execute("SELECT id FROM documents").fetchall()
    ids = {row[0] for row in rows}
    assert {"index", "standard-001", "concept-001"} <= ids
