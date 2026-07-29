import sqlite3
from collections.abc import Iterator
from datetime import date

import pytest

from src.domain.document import OkfDocument
from src.repository.index_builder import build_index


@pytest.fixture
def sample_documents() -> list[OkfDocument]:
    return [
        OkfDocument(
            type="standard",
            id="standard-python-naming",
            title="Pythonコーディング規約",
            summary="Python命名規則を定義する標準",
            status="active",
            owner="platform-team",
            tags=["python", "naming"],
            body="この規約はPythonの命名規則としてPEP8に準拠することを定める。",
            rule_level="must",
            technologies=["python"],
            applies_to=["backend"],
            version="1.0.0",
            effective_date=date(2026, 1, 1),
        ),
        OkfDocument(
            type="standard",
            id="standard-typescript-strict",
            title="TypeScript型安全標準",
            summary="TypeScriptにおける型安全性の標準",
            status="active",
            owner="platform-team",
            tags=["typescript"],
            body="strictモードを有効にし型安全なコードを書くことを定める。",
            rule_level="should",
            technologies=["typescript"],
            applies_to=["frontend"],
            version="1.0.0",
            effective_date=date(2026, 1, 1),
        ),
        OkfDocument(
            type="guideline",
            id="guideline-review",
            title="コードレビューガイドライン",
            summary="コードレビューの進め方に関するガイドライン",
            status="active",
            owner="platform-team",
            tags=["review"],
            body="レビューでは可読性と保守性を重視して指摘を行う。",
        ),
    ]


@pytest.fixture
def seeded_conn(sample_documents: list[OkfDocument]) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    build_index(conn, sample_documents)
    yield conn
    conn.close()
