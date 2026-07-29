# ADR-0001: Phase 1における認証戦略

- **Status:** Accepted
- **Date:** 2026-07-29

---

## Context

CLAUDE.mdの技術スタックでは、FastMCPサーバの認証にAzureProvider（Microsoft Entra ID）を利用する方針が定められている。一方、開発フェーズはPhase 1（PoC基盤構築）とPhase 2（Entra ID認証）に分かれており、Phase 1の時点でEntra IDのテナント・アプリ登録を接続すべきかが未確定だった。

Phase 0のヒアリングで、Entra IDのテナント・アプリ登録自体はすぐに用意できる状態であることを確認した。ただし、Phase 1はPoC基盤（FastMCPサーバ、OKF Parser、SQLite FTS5、MCP Tool）の動作確認が主目的であり、認証接続を必須にするとPhase 1の完了がEntra ID側の準備状況に引きずられるリスクがある。

---

## Decision

Phase 1ではAzureProviderの組み込み（コード上の認証フローの土台）のみ行い、Entra IDへの実接続は行わない。認証の有効/無効は環境変数（`AUTH_ENABLED`、デフォルト`false`）で切り替え、Phase 2で`true`にして実接続を完了させる。

---

## Rationale

Phase 1の目的（PoC基盤が動くことの確認）と、Phase 2の目的（Entra ID認証の実装）を分離することで、Phase 1の完了条件がAzure側の準備状況に依存しなくなる。CLAUDE.mdの「PoCと本番でソースコードを分岐させない」「設定のみでPoCから本番へ移行可能とする」という方針にも合致する。

---

## Options Compared

| Option | Pros | Cons |
|---|---|---|
| **環境変数でAzureProviderの有効/無効を切り替え、Phase 1はfalse固定**（選択） | Phase 1の完了がAzure側準備に依存しない / Phase 2は設定変更のみで本接続に移行できる / ソースコードを分岐させない方針に合致 | 認証まわりのコードはPhase 1時点では未検証のまま残る |
| Phase 1から本番同様にEntra ID接続を有効化する | Phase 1の時点で認証込みの動作確認ができる | Entra ID側のテナント・アプリ登録がPhase 1のブロッカーになりうる / PoC本来のスピード優先の目的に反する |
| AzureProviderの実装自体をPhase 2まで完全に見送る（Phase 1のコードに組み込まない） | Phase 1のスコープが最小になる | Phase 2で認証を後付けする際の設計変更コストが増える / CLAUDE.mdのPoCアーキテクチャ図（AzureProviderが常時スタックに含まれる）と矛盾する |

---

## Trade-offs

**Pros:**
- Phase 1の完了条件がAzure側の準備状況から独立する
- Phase 2への移行が設定変更（環境変数）のみで完結する
- PoCと本番でソースコードを分岐させないというプロジェクト方針を維持できる

**Cons / Constraints:**
- Phase 1時点では認証込みの統合動作は未検証（Phase 2で検証が必要）
- `AUTH_ENABLED=false`時の挙動（認証スキップ）を誤って本番に持ち込まないよう、Phase 2でのデフォルト値見直しが必須

---

## Impact

- Phase 1-1（イシュー#11 基盤セットアップ）: AzureProviderを環境変数で有効/無効切り替え可能な形で組み込む
- Phase 2（イシュー#2）: `AUTH_ENABLED`のデフォルト値・本番設定の見直し、実際のEntra ID接続実装が対象範囲になる
