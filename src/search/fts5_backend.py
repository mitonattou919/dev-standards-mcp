"""SQLite FTS5(BM25)による検索基盤の実装。

メタデータ検索(type/technology/rule_level/status/applies_to)で候補を絞り込んだうえで、
title/summary/bodyに対するBM25全文検索を行う2段階検索。

日本語コンテンツは分かち書きされていないため、標準のunicode61トークナイザでは
文単位で1トークンとして扱われ検索できない。そのためtokenize='trigram'(schema.py)を用い、
3文字以上の部分一致検索を行う。クエリが3文字未満の場合はマッチせず空リストを返す。
"""

import sqlite3

from src.search.backend import SearchQuery, SearchResult

_BASE_SQL = """
SELECT
    documents.id AS id,
    documents.title AS title,
    documents.summary AS summary,
    bm25(documents_fts) AS raw_score
FROM documents_fts
JOIN documents ON documents.rowid = documents_fts.rowid
"""


class Fts5SearchBackend:
    def __init__(self, conn: sqlite3.Connection) -> None:
        conn.row_factory = sqlite3.Row
        self._conn = conn

    def search(self, query: SearchQuery) -> list[SearchResult]:
        clauses = ["documents_fts MATCH ?"]
        params: list[str] = [_to_phrase_match(query.text)]

        if query.type is not None:
            clauses.append("documents.type = ?")
            params.append(query.type)
        if query.rule_level is not None:
            clauses.append("documents.rule_level = ?")
            params.append(query.rule_level)
        if query.status is not None:
            clauses.append("documents.status = ?")
            params.append(query.status)
        if query.technology is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM json_each(documents.technologies) WHERE json_each.value = ?)"
            )
            params.append(query.technology)
        if query.applies_to is not None:
            clauses.append(
                "EXISTS (SELECT 1 FROM json_each(documents.applies_to) WHERE json_each.value = ?)"
            )
            params.append(query.applies_to)

        sql = _BASE_SQL + " WHERE " + " AND ".join(clauses) + " ORDER BY raw_score"

        cursor = self._conn.execute(sql, params)
        return [
            SearchResult(id=row["id"], title=row["title"], summary=row["summary"], score=-row["raw_score"])
            for row in cursor.fetchall()
        ]


def _to_phrase_match(text: str) -> str:
    """クエリ文字列をFTS5のフレーズクエリとして安全にエスケープする(構文エラー・インジェクション対策)。"""
    escaped = text.replace('"', '""')
    return f'"{escaped}"'
