import sqlite3

from src.search.backend import SearchQuery
from src.search.fts5_backend import Fts5SearchBackend


def test_search_matches_query_text(seeded_conn: sqlite3.Connection) -> None:
    backend = Fts5SearchBackend(seeded_conn)

    results = backend.search(SearchQuery(text="命名規則"))

    assert [result.id for result in results] == ["standard-python-naming"]


def test_search_returns_empty_when_no_match(seeded_conn: sqlite3.Connection) -> None:
    backend = Fts5SearchBackend(seeded_conn)

    results = backend.search(SearchQuery(text="存在しないキーワード"))

    assert results == []


def test_search_filters_by_technology(seeded_conn: sqlite3.Connection) -> None:
    backend = Fts5SearchBackend(seeded_conn)

    results = backend.search(SearchQuery(text="型安全", technology="typescript"))

    assert [result.id for result in results] == ["standard-typescript-strict"]


def test_search_filters_by_rule_level(seeded_conn: sqlite3.Connection) -> None:
    backend = Fts5SearchBackend(seeded_conn)

    results = backend.search(SearchQuery(text="型安全", rule_level="should"))

    assert [result.id for result in results] == ["standard-typescript-strict"]


def test_search_filters_by_status(seeded_conn: sqlite3.Connection) -> None:
    backend = Fts5SearchBackend(seeded_conn)

    assert backend.search(SearchQuery(text="型安全", status="active"))
    assert backend.search(SearchQuery(text="型安全", status="deprecated")) == []


def test_search_filters_by_applies_to(seeded_conn: sqlite3.Connection) -> None:
    backend = Fts5SearchBackend(seeded_conn)

    results = backend.search(SearchQuery(text="型安全", applies_to="frontend"))

    assert [result.id for result in results] == ["standard-typescript-strict"]
    assert backend.search(SearchQuery(text="型安全", applies_to="backend")) == []


def test_search_filters_by_type(seeded_conn: sqlite3.Connection) -> None:
    backend = Fts5SearchBackend(seeded_conn)

    results = backend.search(SearchQuery(text="レビュー", type="guideline"))

    assert [result.id for result in results] == ["guideline-review"]


def test_search_result_includes_title_summary_and_score(seeded_conn: sqlite3.Connection) -> None:
    backend = Fts5SearchBackend(seeded_conn)

    results = backend.search(SearchQuery(text="命名規則"))

    assert len(results) == 1
    result = results[0]
    assert result.title == "Pythonコーディング規約"
    assert result.summary == "Python命名規則を定義する標準"
    assert isinstance(result.score, float)
