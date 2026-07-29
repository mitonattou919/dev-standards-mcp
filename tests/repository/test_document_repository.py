import sqlite3

from src.repository.document_repository import SqliteDocumentRepository


def test_get_returns_matching_document(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    document = repository.get("standard-python-naming")

    assert document is not None
    assert document.title == "Pythonコーディング規約"
    assert document.technologies == ["python"]
    assert document.applies_to == ["backend"]
    assert document.tags == ["python", "naming"]


def test_get_returns_none_when_missing(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    assert repository.get("does-not-exist") is None


def test_list_by_metadata_without_filters_returns_all(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    documents = repository.list_by_metadata()

    assert {document.id for document in documents} == {
        "standard-python-naming",
        "standard-typescript-strict",
        "guideline-review",
    }


def test_list_by_metadata_filters_by_type(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    documents = repository.list_by_metadata(type="guideline")

    assert [document.id for document in documents] == ["guideline-review"]


def test_list_by_metadata_filters_by_technology(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    documents = repository.list_by_metadata(technology="typescript")

    assert [document.id for document in documents] == ["standard-typescript-strict"]


def test_list_by_metadata_filters_by_rule_level(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    documents = repository.list_by_metadata(rule_level="must")

    assert [document.id for document in documents] == ["standard-python-naming"]


def test_list_by_metadata_filters_by_status(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    documents = repository.list_by_metadata(status="active")

    assert {document.id for document in documents} == {
        "standard-python-naming",
        "standard-typescript-strict",
        "guideline-review",
    }
    assert repository.list_by_metadata(status="deprecated") == []


def test_list_by_metadata_filters_by_applies_to(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    documents = repository.list_by_metadata(applies_to="frontend")

    assert [document.id for document in documents] == ["standard-typescript-strict"]


def test_list_by_metadata_combines_filters_with_and(seeded_conn: sqlite3.Connection) -> None:
    repository = SqliteDocumentRepository(seeded_conn)

    documents = repository.list_by_metadata(type="standard", technology="python")

    assert [document.id for document in documents] == ["standard-python-naming"]

    no_match = repository.list_by_metadata(type="guideline", technology="python")
    assert no_match == []
