---
type: standard
id: standard-003
title: Dockerコンテナ品質チェック標準
summary: Dockerコンテナを利用するプロジェクトが満たすべき品質チェックの標準。静的解析・依存関係の脆弱性スキャン・ビルド起動検証・イメージスキャンの4層で構成する。
status: active
owner: platform-team
tags:
  - docker
  - container
  - security
  - ci
rule_level: must
technologies:
  - docker
applies_to:
  - containerized-projects
version: "1.0.0"
effective_date: 2026-07-29
---

# Dockerコンテナ品質チェック標準

## このドキュメントについて

Dockerfileやコンテナイメージの品質問題は、レイヤーごとに性質が異なる。書き方の問題（アンチパターン）、依存関係の問題（既知の脆弱性）、動作の問題（そもそも起動しない）はそれぞれ別のチェックでしか検出できないため、単一のツールに頼らず4層に分けてチェックする。

## 1. 静的解析: Hadolint

Dockerfileの書き方そのもの（rootユーザーでの実行、パッケージキャッシュの残存、`latest`タグの使用など）のアンチパターンを検知する。

```bash
docker run --rm -i hadolint/hadolint < Dockerfile
```

**必須度: must**（Dockerfileを変更するすべてのPRで実行する）

## 2. 依存関係の脆弱性スキャン: pip-audit

Pythonの依存関係（`pyproject.toml` / `uv.lock`）に含まれる既知の脆弱性（CVE）を検出する。Dockerビルドを待たずに実行できるため、コンテナ化前から継続的に実行する。

```bash
uv run pip-audit
```

**必須度: must**（プロジェクト全体のDoDとして常時実行する）

## 3. ビルド・起動検証: pytest統合テスト

`docker build` → `docker run` → アプリケーションのヘルスチェック（HTTPリクエストによる応答確認）を自動テストで検証する。Lintや脆弱性スキャンでは「実際に動くか」までは分からないため、動的な検証として別立てで行う。

Dockerが利用できない環境では自動的にスキップする（CI環境では実行される）。

**必須度: must**（`uv run pytest`の一部として実行する）

## 4. コンテナイメージの脆弱性スキャン: Trivy / Docker Scout

ベースイメージやOSパッケージに含まれる既知の脆弱性（CVE）を検出する。`trivy fs`モードを使えば、コンテナイメージだけでなくPython依存関係（項目2）も同一ツールでスキャンでき、将来的な一本化も検討できる。

```bash
trivy image <image-tag>
```

**必須度: should**（本番運用移行（Azure Container Apps）時に`must`へ格上げする）

## クイックリファレンス

| # | チェック内容 | ツール | 検出対象 | 必須度 | 実行タイミング |
|---|-------------|--------|----------|--------|----------------|
| 1 | 静的解析 | Hadolint | Dockerfileのアンチパターン | must | Dockerfile変更時 |
| 2 | 依存関係スキャン | pip-audit | Python依存のCVE | must | 常時（DoD） |
| 3 | ビルド・起動検証 | pytest統合テスト | 実際に起動するか | must | `uv run pytest`実行時 |
| 4 | イメージスキャン | Trivy / Docker Scout | ベースイメージ・OSパッケージのCVE | should → 本番移行時must | Phase 3以降 |
