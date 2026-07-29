---
type: concept
id: glossary-001
title: 用語集
summary: 本プロジェクトで使う主要用語（OKF/MCP/BM25/rule_level）の定義。
status: active
owner: platform-team
tags:
  - glossary
---

# 用語集

## OKF（Open Knowledge Format）

すべてのMarkdownドキュメントが準拠するフロントマター仕様。`type` `id` `title` `summary` `status` `owner` `tags`を必須項目とする。

## MCP（Model Context Protocol）

AIコーディングエージェントが外部ツール・知識ソースと連携するためのプロトコル。本プロジェクトではFastMCPで実装する。

## BM25

全文検索でよく使われるランキングアルゴリズム。単語の出現頻度と文書長を考慮してスコアを算出する。SQLite FTS5が標準で対応する。

## rule_level

標準文書の遵守度合いを示す4段階。

| 値          | 意味                     |
|-------------|--------------------------|
| `must`      | 必ず遵守する               |
| `should`    | 原則として遵守する          |
| `may`       | 任意（推奨に留まる）         |
| `reference` | 参考情報                  |
