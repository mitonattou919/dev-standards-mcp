---
type: example
id: example-001
title: search_standards呼び出し例
summary: MCP Tool `search_standards` を使ってAzure関連の標準を検索する呼び出し例。
status: active
owner: platform-team
tags:
  - mcp-tool
  - search
---

# search_standards 呼び出し例

## 入力

```json
{
  "query": "リソース命名",
  "technology": "azure",
  "rule_level": "must"
}
```

## 出力（イメージ）

```json
[
  {
    "id": "standard-001",
    "title": "Azureリソースネーミング規約",
    "summary": "Azureリソースの命名パターンと必須タグを定めた規約。",
    "score": 8.42
  }
]
```

## ポイント

- `technology`と`rule_level`はメタデータ検索（絞り込み）に使われる
- `query`はBM25による全文検索（title/summary/body対象）に使われる
