# 開発標準 MCP 実装ガイドライン

## 目的

本プロジェクトは、社内開発標準をAIコーディングエージェントが一貫して参照・遵守できるMCP（Model Context Protocol）サーバを構築することを目的とする。

設計方針は以下の通りとする。

* GitHubを知識の正本（Single Source of Truth）とする
* AIエージェントはMCP経由でのみ知識を取得する
* 人間とAIが同一の知識を参照できる構成とする
* 検索基盤は将来的に置き換え可能な構成とする
* PoCと本番でソースコードを分岐させない

---

# アーキテクチャ

```text
                GitHub (本番)
                     │
                     │
      sample-knowledge (PoC)
                     │
                     ▼
              OKF Parser
                     │
                     ▼
          SQLite FTS5 (BM25)
                     │
                     ▼
                FastMCP
                     │
                     ▼
    Claude Code / Codex / Copilot
```

---

# 技術スタック

| 項目            | 採用技術                                           |
| ------------- | ---------------------------------------------- |
| 言語            | Python 3.13以上                                  |
| パッケージ管理       | **uv**                                         |
| MCP Framework | FastMCP                                        |
| 認証            | FastMCP AzureProvider + Microsoft Entra ID     |
| コンテナ          | Docker                                         |
| 実行環境          | ローカルDocker（PoC）→ Azure Container Apps          |
| 検索            | SQLite FTS5（BM25）                              |
| 正本            | GitHub Repository                              |
| ドキュメント形式      | Open Knowledge Format (OKF) + Optional Profile |

---

# Python開発ポリシー

Pythonプロジェクトは **uv** を利用すること。

以下は採用しない。

* pipベースの環境構築
* requirements.txtを前提とした依存管理
* 手動venv構築

依存関係は **pyproject.toml** に定義する。

環境構築は以下を利用する。

```bash
uv sync
```

スクリプト実行は以下を利用する。

```bash
uv run <command>
```

---

# ディレクトリ構成

```text
dev-standards-mcp/

├── sample-knowledge/
│   ├── index.md
│   ├── standards/
│   ├── guidelines/
│   ├── checklists/
│   ├── templates/
│   ├── examples/
│   └── glossary/
│
├── src/
│   ├── api/
│   ├── auth/
│   ├── domain/
│   ├── parser/
│   ├── repository/
│   ├── resources/
│   ├── search/
│   ├── services/
│   └── tools/
│
├── tests/
│
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# GitHub（本番）

知識の正本はGitHub Repositoryとする。

```text
dev-standards/

├── index.md
├── log.md
│
├── standards/
├── guidelines/
├── checklists/
├── templates/
├── decisions/
├── examples/
└── glossary/
```

---

# Open Knowledge Format

すべてのMarkdownはOpen Knowledge Formatに準拠する。

さらにOptional Profileとして以下を採用する。

## 必須項目

```yaml
type
id
title
summary
status
owner
tags
```

## type=standard の追加必須項目

```yaml
rule_level
technologies
applies_to
version
effective_date
```

---

# type一覧

```text
standard
guideline
decision
template
checklist
reference
example
concept
howto
exception
```

---

# rule_level

```text
must
should
may
reference
```

mustは必ず遵守すること。

---

# SQLite

SQLiteは検索インデックスであり、正本ではない。

以下を前提とする。

* 再生成可能であること
* 永続化を前提としない
* GitHubまたはsample-knowledgeから生成する

---

# 検索方式

SQLite FTS5(BM25)を利用する。

検索は以下の2段階で行う。

## 1. メタデータ検索

対象

* type
* technologies
* status
* applies_to
* rule_level

## 2. BM25全文検索

対象

* title
* summary
* body

---

# MCP Tool

最低限以下を実装する。

```text
search_standards
get_standard
get_applicable_standards
get_review_checklist
```

将来的に追加する。

```text
check_standard_compliance
refresh_index
```

---

# Tool仕様

## search_standards

### 入力

```text
query
technology
rule_level
```

### 出力

```text
id
title
summary
score
```

---

## get_standard

### 入力

```text
id
```

### 出力

Markdown本文

---

## get_applicable_standards

### 入力

```text
project
files
task
```

### 出力

```text
must
should
reference
```

---

## get_review_checklist

レビュー用チェックリストを返却する。

---

# 認証

FastMCP AzureProviderを利用する。

認証はFastMCP側で実施する。

Azure Container AppsのEasy Authは利用しない。

## ローカル

```text
localhost
    │
AzureProvider
    │
Entra ID
```

## Azure

```text
ACA
   │
AzureProvider
   │
Entra ID
```

---

# PoC

PoCではGitHubとの同期は実装しない。

ローカルに配置した **sample-knowledge** を読み込む。

```text
                 ローカル開発環境

Coding Agent
      │
      ▼
localhost:8000/mcp
      │
      ▼
Docker
      │
      ▼
FastMCP
 ├─ AzureProvider
 ├─ OKF Parser
 ├─ SQLite FTS5
 └─ MCP Tools
      │
      ▼
sample-knowledge/
```

sample-knowledgeは本番GitHubと同一のOKF Profileに準拠すること。

SQLiteはコンテナローカルへ生成する。

---

# Azure Container Apps

PoC完了後はAzure Container Appsへ配置する。

```text
Coding Agent
      │
      ▼
Azure Container Apps
      │
      ▼
FastMCP
      │
      ▼
SQLite
      │
      ▼
GitHub
```

設定

```text
minReplicas = 1
maxReplicas = 1
```

SQLiteはコンテナローカルへ配置する。

---

# 環境切替

PoCと本番でソースコードは変更しない。

差分は設定のみとする。

## PoC

```yaml
knowledge:
  source: sample
  path: ./sample-knowledge
```

## 本番

```yaml
knowledge:
  source: github
  repository: dev-standards
```

---

# CI/CD（将来）

GitHub Actionsで以下を実施する。

* OKF Validation
* YAML Validation
* Link Check
* SQLite Index Build
* Docker Build
* Container Registry Push
* Azure Container Apps Deploy

---

# 実装ポリシー

* Repository Patternを採用する
* Domain Modelを分離する
* ToolからSQLiteへ直接アクセスしない
* Parser・Search・Repository・Toolを疎結合にする
* 検索基盤は抽象化し、SQLiteからAzure AI Search等へ容易に差し替え可能とする
* GitHubを唯一の正本とする
* SQLiteは検索インデックスとして扱う
* MCP Toolは検索基盤に依存しないインターフェースを提供する
* PoCと本番でソースコードを分岐させない
* 設定のみでPoCから本番へ移行可能とする

---

# 開発フェーズ

## Phase 1

* uv
* FastMCP
* AzureProvider
* OKF Parser
* SQLite FTS5
* sample-knowledge対応
* ローカルDocker

## Phase 2

* Microsoft Entra ID認証
* Tool充実
* SQLite最適化

## Phase 3

* Azure Container Apps
* Azure Key Vault
* GitHub連携

## Phase 4

* GitHub Actions
* 自動デプロイ
* 自動インデックス生成

## Phase 5

必要に応じて検索基盤をAzure AI Search等へ置き換える。

---

# 完了基準（Definition of Done）

各Issue・PRは、クローズ/マージ前に以下を満たすこと。

* `uv run ruff check .` で静的解析エラーがないこと
* `uv run mypy .` で型チェックエラーがないこと（strictモード）
* `uv run pytest` でユニットテストが全て通過すること
* テストカバレッジ70%以上であること（`--cov-fail-under=70`で自動チェック）
  * 70%はPoC期間中の基準値。本番運用移行時に見直すこと

---

# 非機能要件

* FastMCPはステートレスであること
* コンテナはイミュータブルであること
* SQLiteは再生成可能であること
* GitHubのMarkdownを唯一の正本とすること
* エージェントはGitHubを直接参照せず、必ずMCP Tool経由で知識を取得すること
* MCP Toolのインターフェースは検索基盤変更後も維持すること
* PoCと本番で同一コードベースを維持すること

