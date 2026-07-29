# プロジェクトコンテキスト

Phase着手前のヒアリング（`/grilling`）で確定した要件・前提をまとめる。随時更新。

## Phase 0: Phase 1着手前ヒアリング（2026-07-29）

関連Issue: [#6](https://github.com/mitonattou919/dev-standards-mcp/issues/6)

### 決定事項

1. **sample-knowledgeの内容**: ダミードキュメントをベースに、ユーザーが作成した実ドキュメント（Azureネーミングルール等）を数点混在させる。評価の高速化が狙い。
2. **Entra ID接続**: Phase 1では未接続。テナント・アプリ登録自体はすぐ作れる状態だが、意図的にPhase 1のスコープ外とする。詳細は [ADR-0001](./ADR/adr-0001-phase1-auth-strategy.md) 参照。
3. **ローカルDocker実行**: 単体`docker run`（`docker compose`は使わない）。コンテナは1つ（FastMCPサーバのみ）で、将来のAzure Container Apps（`minReplicas=1`/`maxReplicas=1`のシングルコンテナ）構成に近い形にする。
4. **FastMCPバージョン / 認証切り替え**: 最新安定版を`uv add fastmcp`で導入し、明示的なバージョン固定はしない（`uv.lock`に委ねる）。認証の有効/無効は環境変数で切り替える。詳細は [ADR-0001](./ADR/adr-0001-phase1-auth-strategy.md) 参照。
5. **OKF `id`採番規則**: `{type}-{連番3桁}`（例: `standard-001`, `guideline-001`）。
6. **Phase 1サブイシュー着手順**: [#11](https://github.com/mitonattou919/dev-standards-mcp/issues/11) → [#7](https://github.com/mitonattou919/dev-standards-mcp/issues/7) → [#8](https://github.com/mitonattou919/dev-standards-mcp/issues/8) → [#9](https://github.com/mitonattou919/dev-standards-mcp/issues/9) → [#10](https://github.com/mitonattou919/dev-standards-mcp/issues/10)。依存関係が一直線のため決め打ち。

### 未決事項

現時点で特になし。Phase 1着手前の主要な曖昧点は解消済み。
