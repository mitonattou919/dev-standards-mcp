# dev-standards-mcp

社内開発標準をAIコーディングエージェントが一貫して参照・遵守できるMCP（Model Context Protocol）サーバ。

詳細な設計方針は [CLAUDE.md](./CLAUDE.md) を参照。

## セットアップ（ローカル / uv）

```bash
uv sync
```

## 起動（ローカル / uv）

```bash
uv run python main.py
```

デフォルトでは `http://127.0.0.1:8000/mcp` で待ち受ける。`sample-knowledge/` の内容から起動時にオンメモリでSQLite FTS5インデックスを構築する。

## 起動（Docker）

イメージのビルド:

```bash
docker build -t dev-standards-mcp:local .
```

コンテナの起動:

```bash
docker run --rm -p 8000:8000 dev-standards-mcp:local
```

`http://localhost:8000/mcp` にMCPクライアント（Claude Code等）から接続できる。

## MCPクライアントからの動作確認

コンテナ（またはローカルの`uv run python main.py`）を起動した状態で、以下のいずれかの方法で疎通・Tool呼び出しを確認できる。

### 方法A: Claude Code から接続

```bash
claude mcp add --transport http dev-standards-mcp http://localhost:8000/mcp
```

追加後、Claude Codeのセッション内で `/mcp` と入力すると接続状態（`dev-standards-mcp` が `connected`）を確認できる。開発標準に関する質問（例: 「Dockerの品質チェックで何をすればいい？」）を投げると、`search_standards` 等のToolが自動的に呼び出される。

不要になったら以下で削除する。

```bash
claude mcp remove dev-standards-mcp
```

### 方法B: MCP Inspector（GUIで対話的に確認）

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

ブラウザが開き、`search_standards` / `get_standard` / `get_applicable_standards` / `get_review_checklist` の4 Toolを一覧・実行できる。

### 方法C: curlで直接JSON-RPCを叩く（ツール不要）

MCPのStreamable HTTPトランスポートはセッションIDを要求するため、`initialize`のレスポンスヘッダーから`Mcp-Session-Id`を取り出して以降のリクエストに付与する。

```bash
# 1. initialize してセッションIDを取得
curl -sD /tmp/mcp_headers.txt http://localhost:8000/mcp -X POST \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"manual-check","version":"1.0"}}}'
SESSION_ID=$(grep -i "mcp-session-id" /tmp/mcp_headers.txt | awk '{print $2}' | tr -d '\r')

# 2. initialized通知を送る（レスポンスなし・202が返る）
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8000/mcp -X POST \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'

# 3. search_standards を呼び出す
curl -s http://localhost:8000/mcp -X POST \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_standards","arguments":{"query":"docker"}}}'
```

`standard-003`（Dockerコンテナ品質チェック標準）がヒットすれば、コンテナ起動→インデックス構築→検索まで一連の動作確認が取れたことになる。

## 環境変数

| 変数名 | デフォルト | 説明 |
| --- | --- | --- |
| `KNOWLEDGE_SOURCE` | `sample` | 知識ソース。PoCでは`sample`のみ対応 |
| `KNOWLEDGE_PATH` | `./sample-knowledge` | 知識ディレクトリのパス |
| `AUTH_ENABLED` | `false` | `true`にするとAzureProvider認証を有効化（`AZURE_CLIENT_ID`等が必須） |
| `MCP_HOST` | `127.0.0.1`（Dockerイメージ内では`0.0.0.0`） | 待ち受けホスト |
| `MCP_PORT` | `8000` | 待ち受けポート |

## 開発

```bash
uv run ruff check .
uv run mypy .
uv run pytest
uv run pip-audit
```

`uv run pytest` にはDockerイメージのbuild・run・MCPヘルスチェックを行う統合テスト（`tests/test_docker_integration.py`）が含まれる。Dockerが利用できない環境では自動的にスキップされる。

Dockerfileを変更した場合は、Hadolintでの静的解析も実行すること。

```bash
docker run --rm -i hadolint/hadolint < Dockerfile
```

## ナレッジの執筆

`sample-knowledge/` へOKF文書を追加・更新するときは、Claude Codeのプロジェクトスキル `okf-authoring`（`.claude/skills/okf-authoring/SKILL.md`）を使う。既存文書の検索による重複回避、type別の配置先とID採番、必須項目の充足、`index.md` の索引更新、検証、PR作成までを手順化してある。

```
/okf-authoring
```

このスキルはプロジェクトスコープのため、本リポジトリ内で作業しているときのみ起動する。他リポジトリで得た実践知を書き戻す場合は、出所（リポジトリ・コミットSHA等）を入力として渡すこと。
