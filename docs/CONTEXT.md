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

## Phase 1.5: ナレッジ拡充・実運用評価循環ヒアリング（2026-07-29）

関連Issue: [#26](https://github.com/mitonattou919/dev-standards-mcp/issues/26)（サブIssue: [#27](https://github.com/mitonattou919/dev-standards-mcp/issues/27) [#28](https://github.com/mitonattou919/dev-standards-mcp/issues/28) [#29](https://github.com/mitonattou919/dev-standards-mcp/issues/29) [#30](https://github.com/mitonattou919/dev-standards-mcp/issues/30)）

### 背景

Phase 1完了後、次のアクションとしてAzure Container Apps移行（Phase 2/3）を想定していたが、ローカルDocker実行が既に準本番相当の運用に耐えうると気づき、ロードマップを見直した。

### 決定事項

1. **評価の目的**: 単一指標ではなく、循環プロセス全体をざっくり評価する。加えてMCP検索経由の参照と「直参照スキル」（MCPなしでgrep/Readする素の探索）とで、トークン/コンテキスト使用量の差異も比較する。
2. **比較ベースライン**: 全量ロード方式は比較対象としない。MCPなしで都度探索させる「直参照スキル」を新規に作成し、それと比較する（[#28](https://github.com/mitonattou919/dev-standards-mcp/issues/28)）。
3. **ナレッジベースの本質的価値**: 既存の実ドキュメントを移植しても組織固有の"色"は薄いと判明。価値は「執筆スキルで一緒に書く→使う→実践知を書き戻す」循環プロセスそのものと、それによる開発品質・再現性向上にある。組織色はこの循環から事後的に滲み出るものと捉える。
4. **循環を回す場**: 実質、人間一人＋エージェント。特定の実プロジェクトを最初から使うのではなく、新規に「OTel Collector＋ダッシュボード」計測基盤プロジェクトを起動し、これを循環の最初の実験台とする（[#30](https://github.com/mitonattou919/dev-standards-mcp/issues/30)）。循環の型が固まった後、本命であるFastAPI+HTMX（Webアプリ）／Bicep（Azureリソース、Webアプリのホスト先）のプロジェクトへ展開する。
5. **第一実験台プロジェクトの評価姿勢**: 定量評価にはこだわらない（計測基盤がまだ無いため）。循環がちゃんと回るかを定性的に見る。
6. **Phase 2/3（Entra ID認証・Azure移行）の扱い**: 凍結せず、Issue #2 / #3 はそのまま残す。Azure側の技術検証は別PoC（MCPのAzure Container Apps + AzureProviderホスティング）で完了済みのため技術的ブロッカーはない。ただし着手を強制する強いトリガーはなく（ローカルコンテナでも複数人展開は可能なため）、opportunistic（気が向いたら着手）扱いとする。
7. **Phase 1.5の区切り**: 循環（書く→使う→書き戻す）を2〜3周実施したら [#26](https://github.com/mitonattou919/dev-standards-mcp/issues/26) はクローズする。ただし循環活動自体はIssueクローズ後もPhaseの枠を超えて継続する。
8. **トークン/コンテキスト計測基盤**: OpenTelemetryでローカルにCollectorを立て、JSON等にエクスポートし、簡易ダッシュボード（Aspire Dashboard等のOSS）で可視化する（[#29](https://github.com/mitonattou919/dev-standards-mcp/issues/29)）。循環検証（[#27](https://github.com/mitonattou919/dev-standards-mcp/issues/27) [#30](https://github.com/mitonattou919/dev-standards-mcp/issues/30)）とは並行・独立で進める。

### 未決事項

- OTel計測基盤で実際にどの粒度のメトリクスを比較するか（トークン数のみか、レイテンシ・ツール呼び出し回数等も含めるか）は着手時に詰める。
- OKF type一覧のうち `decision` / `howto` / `exception` を使うかは、実際に書く実践知の性質を見てから判断する。`concept` は glossary-001 と concept-001 で、`reference` は index.md で使用済み。

## Phase 1.5-5: 軽量なエージェント駆動開発フローconceptの導入（2026-08-02）

関連Issue: [#34](https://github.com/mitonattou919/dev-standards-mcp/issues/34) / 関連Discussion: [#33](https://github.com/mitonattou919/dev-standards-mcp/discussions/33)

### 背景

Discussion #33 で提案した実践知循環型の開発フレームワーク（全19章）を一括で確定版として導入すると、実践検証を経ていない設計まで規範化される。まず薄い `concept` 1本で循環を開始し、観測結果から文書構成とProfileを固める方針とした。

### 決定事項

1. **配置先**: `sample-knowledge/concepts/` を新設する。既存ディレクトリへの相乗りはしない。
2. **ID採番**: 新規conceptは `concept-001` とする。IDのprefixは `type` と一致させる（Phase 0 決定事項5の補足）。
3. **glossary-001 の扱い**: `type: concept` / `id: glossary-001` はPhase 1期の例外として、ID・配置ともに現状維持する。IDの変更は検索インデックスと既存の相互参照を壊す一方、実害がないため。
4. **concept-001 の status**: `draft` とする。仮説検証用の定義であり、確定した標準ではない。
5. **evidenceの最小フォーマット**: PR本文へYAMLブロックで記載する。参照（コミットSHA / working tree状態 / 参照方式 / 参照文書ID）、適用、適用不能・逸脱の3節。現段階では**記載の有無のみを決定論的に確認**し、内容の妥当性評価はスコープ外とする。定義は concept-001 に置く。
6. **公開前提**: 現段階の知識データ・観測ログはすべて公開扱いとする。非公開情報の取り扱いは循環の型が固まった後に定義する。

### 未決事項

- 観測結果を踏まえてconcept-001をどこまで分割・昇格（`status: active` / `standard` 化）するかは、循環1周目（[#30](https://github.com/mitonattou919/dev-standards-mcp/issues/30)）の結果を見てから判断する。
