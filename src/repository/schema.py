"""SQLiteスキーマ定義。SQLiteは検索インデックスであり正本ではないため、常に再生成可能とする。"""

CREATE_DOCUMENTS_TABLE = """
CREATE TABLE documents (
    rowid INTEGER PRIMARY KEY,
    id TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL,
    owner TEXT NOT NULL,
    tags TEXT NOT NULL,
    body TEXT NOT NULL,
    rule_level TEXT,
    technologies TEXT,
    applies_to TEXT,
    version TEXT,
    effective_date TEXT
)
"""

CREATE_FTS_TABLE = """
CREATE VIRTUAL TABLE documents_fts USING fts5(
    title, summary, body,
    content='documents',
    content_rowid='rowid',
    tokenize='trigram'
)
"""

DROP_FTS_TABLE = "DROP TABLE IF EXISTS documents_fts"
DROP_DOCUMENTS_TABLE = "DROP TABLE IF EXISTS documents"

INSERT_DOCUMENT = """
INSERT INTO documents (
    id, type, title, summary, status, owner, tags, body,
    rule_level, technologies, applies_to, version, effective_date
) VALUES (
    :id, :type, :title, :summary, :status, :owner, :tags, :body,
    :rule_level, :technologies, :applies_to, :version, :effective_date
)
"""

REBUILD_FTS_INDEX = "INSERT INTO documents_fts(documents_fts) VALUES ('rebuild')"
