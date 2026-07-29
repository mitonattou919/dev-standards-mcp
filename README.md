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
