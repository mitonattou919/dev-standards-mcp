import sqlite3
from collections.abc import Iterator
from datetime import date

import pytest

from src.domain.document import OkfDocument
from src.repository.document_repository import SqliteDocumentRepository
from src.repository.index_builder import build_index
from src.search.fts5_backend import Fts5SearchBackend
from src.services.standards_service import StandardsService


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


@pytest.fixture
def applicability_documents() -> list[OkfDocument]:
    return [
        OkfDocument(
            type="standard",
            id="standard-all-python",
            title="全プロジェクト向けPython標準",
            summary="全プロジェクトに適用されるPython標準",
            status="active",
            owner="platform-team",
            tags=["python"],
            body="Pythonプロジェクト全体に適用する共通ルールを定める。",
            rule_level="must",
            technologies=["python"],
            applies_to=["all-projects"],
            version="1.0.0",
            effective_date=date(2026, 1, 1),
        ),
        OkfDocument(
            type="standard",
            id="standard-backend-azure",
            title="バックエンドAzure標準",
            summary="backendプロジェクト向けAzure標準",
            status="active",
            owner="platform-team",
            tags=["azure"],
            body="バックエンドプロジェクトにおけるAzureリソースの取り扱いを定める。",
            rule_level="should",
            technologies=["azure"],
            applies_to=["backend"],
            version="1.0.0",
            effective_date=date(2026, 1, 1),
        ),
        OkfDocument(
            type="standard",
            id="standard-frontend-typescript",
            title="フロントエンドTypeScript標準",
            summary="frontendプロジェクト向けTypeScript標準",
            status="active",
            owner="platform-team",
            tags=["typescript"],
            body="フロントエンドプロジェクトにおけるTypeScriptの型安全性を定める。",
            rule_level="must",
            technologies=["typescript"],
            applies_to=["frontend"],
            version="1.0.0",
            effective_date=date(2026, 1, 1),
        ),
        OkfDocument(
            type="standard",
            id="standard-general-reference",
            title="一般リファレンス",
            summary="技術非依存の一般リファレンス",
            status="active",
            owner="platform-team",
            tags=["general"],
            body="技術に依存しない一般的な参考情報をまとめる。",
            rule_level="reference",
            technologies=None,
            applies_to=None,
            version=None,
            effective_date=None,
        ),
        OkfDocument(
            type="standard",
            id="standard-optional-python",
            title="任意のPython推奨事項",
            summary="MAYレベルのPython推奨事項",
            status="active",
            owner="platform-team",
            tags=["python"],
            body="Pythonにおける任意の推奨プラクティスをまとめる。",
            rule_level="may",
            technologies=["python"],
            applies_to=["all-projects"],
            version="1.0.0",
            effective_date=date(2026, 1, 1),
        ),
        OkfDocument(
            type="checklist",
            id="checklist-service-test",
            title="サービステスト用チェックリスト",
            summary="get_review_checklistのテスト用チェックリスト",
            status="active",
            owner="platform-team",
            tags=["checklist"],
            body="- [ ] チェック項目1\n- [ ] チェック項目2",
        ),
        OkfDocument(
            type="standard",
            id="standard-inactive",
            title="非アクティブ標準",
            summary="statusがactiveでない標準",
            status="deprecated",
            owner="platform-team",
            tags=["deprecated"],
            body="廃止されたAzure標準の名残。",
            rule_level="must",
            technologies=None,
            applies_to=["all-projects"],
            version="1.0.0",
            effective_date=date(2026, 1, 1),
        ),
    ]


@pytest.fixture
def standards_service(applicability_documents: list[OkfDocument]) -> Iterator[StandardsService]:
    conn = sqlite3.connect(":memory:")
    build_index(conn, applicability_documents)
    repository = SqliteDocumentRepository(conn)
    search_backend = Fts5SearchBackend(conn)
    yield StandardsService(repository, search_backend)
    conn.close()
