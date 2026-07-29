"""検索基盤の抽象インターフェース。SQLite FTS5に限定されず、将来Azure AI Search等へ差し替え可能にする。"""

from dataclasses import dataclass
from typing import Protocol

from src.domain.document import DocumentType, RuleLevel


@dataclass(frozen=True)
class SearchQuery:
    text: str
    type: DocumentType | None = None
    technology: str | None = None
    rule_level: RuleLevel | None = None
    status: str | None = None
    applies_to: str | None = None


@dataclass(frozen=True)
class SearchResult:
    id: str
    title: str
    summary: str
    score: float


class SearchBackend(Protocol):
    def search(self, query: SearchQuery) -> list[SearchResult]: ...
